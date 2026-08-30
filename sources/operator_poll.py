"""
Source module that polls bpy.context.window_manager.operators and emits an "operator" AchievementEvent for any new operator calls.

Also tracks the selection's median world-space position, attaching how far it moved since the last completed action to each event's `extra` dict (as "selection_delta"). This exists because interactive/modal transform operators (extrude+move, duplicate+move, etc.) don't reliably expose the actual distance moved through their own properties. Only sampled/updated when a new operator is actually detected, never on idle ticks - bpy.app.timers keeps firing while a modal drag is still in progress, and sampling then would silently overwrite the baseline with a not-yet-final position.

Also tracks the mesh's total vertex/edge/face counts the same way, attaching how many of each were added since the last completed action (as "vert_count_delta"/"edge_count_delta"/"face_count_delta"). This exists because "did this action create N edges" can't be answered reliably by checking bl_idname + selection mode - e.g. MESH_OT_edge_face_add is normally invoked from Vertex select mode, and extruding a lone vertex still shows up as MESH_OT_extrude_region_move regardless of what ends up selected afterward. Measuring the actual topology change directly sidesteps needing to infer intent from mode/selection state at all - the mesh either gained edges or it didn't.

Also tracks a cheap signature (bl_idname + properties) of the top-of-history operator (wm.operators[-1]) on every tick, exposed via get_last_redo_panel_adjustment_time(). Editing the "adjust last operation" redo panel doesn't add a new entry to wm.operators - it pops the last one internally and pushes a fresh one right back, netting the same count - but it DOES change that entry's properties in place. Comparing the signature tick-to-tick catches this even though the count never changes. This exists for undo_redo_watch.py: bpy.context.window_manager.operators isn't reliably readable from inside bpy.app.handlers.undo_pre/undo_post (mirrors the _RestrictData issue toast.py hit during register()), but it's fine from this module's timer context, so this is the one place that's allowed to read it for that purpose.
"""



import time

import bpy
import bmesh
import mathutils

from .. import manager
from ..events import AchievementEvent

# Get operator count
_last_op_count: int = 0

# Median position of the current selection, as of the last completed action
_last_median: mathutils.Vector | None = None

# (vert_count, edge_count, face_count) of the edited mesh, as of the
# last completed action
_last_mesh_counts: tuple | None = None

# Signature (bl_idname, repr(properties)) of wm.operators[-1] as of the
# last poll tick, used to detect in-place edits (redo panel) even when
# the operator count doesn't change
_last_top_signature: tuple | None = None

# time.time() of the last detected redo-panel-style in-place edit
_last_redo_panel_adjustment_time: float = 0.0

# Interval for each poll
POLL_INTERVAL: float = 0.5



def _get_selection_median(context: bpy.types.Context):
    """Returns the median world-space position of the current selection.
    Works for edit-mesh (selected vertices) and object mode (selected
    objects). Returns None if there's nothing to measure."""

    obj = context.active_object
    if obj is None:
        return None

    # Edit-mesh selection
    if obj.mode == 'EDIT' and obj.type == 'MESH':
        bm = bmesh.from_edit_mesh(obj.data)
        selected = [v for v in bm.verts if v.select]
        if not selected:
            return None

        local_median = sum((v.co for v in selected), mathutils.Vector()) / len(selected)
        return obj.matrix_world @ local_median

    # Object mode fallback - median of selected objects' world positions
    selected_objs = context.selected_objects
    if not selected_objs:
        return None

    return sum((o.matrix_world.translation for o in selected_objs), mathutils.Vector()) / len(selected_objs)

def _get_mesh_element_counts(context: bpy.types.Context):
    """Returns (vert_count, edge_count, face_count) for the mesh
    currently being edited, or None if not in mesh edit mode. Used to
    measure actual topology changes directly, rather than inferring
    them from operator name + selection mode."""

    obj = context.active_object
    if obj is None or obj.mode != 'EDIT' or obj.type != 'MESH':
        return None

    bm = bmesh.from_edit_mesh(obj.data)
    return (len(bm.verts), len(bm.edges), len(bm.faces))

def _extract_properties(props_struct) -> dict:
    """Extract properties and values from operators and their nested operators for easier reading."""

    result = {}
    for prop in props_struct.bl_rna.properties:
        identifier = prop.identifier

        # Meta property present on every struct, never useful here
        if identifier == "rna_type":
            continue

        value = getattr(props_struct, identifier)

        if prop.type == 'POINTER':
            if "_OT_" in identifier and isinstance(value, bpy.types.bpy_struct):
                result[identifier] = _extract_properties(value)
            continue

        if isinstance(value, (mathutils.Vector, mathutils.Euler, mathutils.Color)):
            result[identifier] = tuple(value)
        elif hasattr(value, "__len__") and not isinstance(value, str):
            try:
                result[identifier] = tuple(value)
            except TypeError:
                result[identifier] = value
        else:
            result[identifier] = value

    return result

def _signature_for(op) -> tuple:
    """A cheap, comparable snapshot of an operator's identity + current
    property values, used to detect when the SAME history entry gets
    silently edited in place (redo panel) rather than a new one appearing."""

    return (op.bl_idname, repr(_extract_properties(op.properties)))

def get_last_redo_panel_adjustment_time() -> float:
    """time.time() of the last detected in-place redo-panel edit, or 0.0
    if none has been seen yet. undo_redo_watch.py uses this to tell a
    genuine undo apart from a redo-panel edit, since it can't reliably
    read wm.operators from inside its own handler callbacks."""

    return _last_redo_panel_adjustment_time

def _poll() -> float:
    """Poll bpy.context.window_manager.operators to get the last action performed by the user. Returns the interval."""

    # Get the global operator count, last-known selection median, and last-known mesh counts
    global _last_op_count, _last_median, _last_mesh_counts, _last_top_signature, _last_redo_panel_adjustment_time

    # Get the window manager, do nothing if it can't be found
    wm = bpy.context.window_manager
    if wm is None:
        return POLL_INTERVAL

    # Get the current window's operators
    ops = wm.operators
    current_count = len(ops)

    # If another operator was run
    if current_count > _last_op_count:
        # Sample the selection's position and mesh element counts now -
        # right after the new operator(s) actually completed - and
        # compare against the baseline from the last completed action,
        # not from idle ticks (see module docstring)
        current_median = _get_selection_median(bpy.context)
        current_mesh_counts = _get_mesh_element_counts(bpy.context)

        # Get the new operations
        new_ops = ops[_last_op_count:current_count]

        extra = {}
        if _last_median is not None and current_median is not None:
            extra["selection_delta"] = (current_median - _last_median).length

        if _last_mesh_counts is not None and current_mesh_counts is not None:
            extra["vert_count_delta"] = current_mesh_counts[0] - _last_mesh_counts[0]
            extra["edge_count_delta"] = current_mesh_counts[1] - _last_mesh_counts[1]
            extra["face_count_delta"] = current_mesh_counts[2] - _last_mesh_counts[2]

        # Emit an event for each operator
        for op in new_ops:
            # Print operator name
            print(f"\n{op.bl_idname}")

            print("- Props")
            props = _extract_properties(op.properties)
            for k, v in props.items():
                print(f"  - {k}: {v}")

            print("- Extras")
            for k, v in extra.items():
                print(f"  - {k}: {v}")
                
            event = AchievementEvent(
                type="operator",
                bl_idname=op.bl_idname,
                properties=props,
                op=op,
                extra=extra,
            )

            # Send the event to the manager
            manager.handle_event(event)

        # New baselines are "state right after this batch of actions"
        _last_median = current_median
        _last_mesh_counts = current_mesh_counts

        # Refresh the top-of-history signature to match the new last entry
        if current_count > 0:
            _last_top_signature = _signature_for(ops[-1])

    elif current_count > 0:
        # No new entry, but check whether the existing top entry's
        # properties changed in place - this is exactly what happens when
        # the user edits the "adjust last operation" redo panel: same
        # count, different values
        new_signature = _signature_for(ops[-1])
        if _last_top_signature is not None and new_signature != _last_top_signature:
            _last_redo_panel_adjustment_time = time.time()
        _last_top_signature = new_signature

    # Update the count
    _last_op_count = current_count
    return POLL_INTERVAL

def register():
    """Register the source."""

    global _last_op_count, _last_median, _last_mesh_counts, _last_top_signature, _last_redo_panel_adjustment_time
    _last_op_count = 0
    _last_median = None
    _last_mesh_counts = None
    _last_top_signature = None
    _last_redo_panel_adjustment_time = 0.0
    if not bpy.app.timers.is_registered(_poll):
        bpy.app.timers.register(_poll, first_interval=1.0, persistent=True)

def unregister():
    """Unregister the source."""

    if bpy.app.timers.is_registered(_poll):
        bpy.app.timers.unregister(_poll)
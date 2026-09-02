"""
Watches the list of operators processed by Blender and fires events with as much detail about the operator and the options associated with it as it can find.

## Format of Operator Event

### type
Declares the event type as "operator".

### bl_idname
The constant ID name of the operator performed.

### properties
A dictionary of properties associated with the operation, usually contains useful information about the behavior of the operation.

### op
The raw operator object itself.

###extra
Extra data added manually to fix shortcomings of the properties.
"""



import time

import bpy
import bmesh
import mathutils

from .. import manager
from ..events import AchievementEvent

# Track last operator count to determine which operator to pull
_last_op_count: int = 0

# Median position of the current selection, as of the last completed action
_last_median: mathutils.Vector | None = None

# Tracker for the vert/edge/face count of the selected mesh as of the last action
_last_mesh_counts: tuple | None = None

# Track last operator to help prevent false-positive undo tracking
_last_top_signature: tuple | None = None

# Track the time of the last detected modify panel edit
_last_redo_panel_adjustment_time: float = 0.0

# Interval time for each poll
POLL_INTERVAL: float = 0.5



def _get_selection_median(context: bpy.types.Context):
    """Returns the median world-space position of the current selection."""

    # Get the selected object
    obj: bpy.types.Object = context.active_object
    if obj is None:
        return None

    # If in Edit Mode on a mesh, calculate median of selected verts
    if obj.mode == "EDIT" and obj.type == "MESH":
        bm: bmesh.types.BMesh = bmesh.from_edit_mesh(obj.data)

        # Get selected verticies
        selected: list[bmesh.types.BMVert]  = [v for v in bm.verts if v.select]
        if not selected:
            return None

        # Calculate the median
        local_median = sum((v.co for v in selected), mathutils.Vector()) / len(selected)
        return obj.matrix_world @ local_median

    if obj.mode == "EDIT" and obj.type == "ARMATURE":
        points = []
        for bone in obj.data.edit_bones:
            if bone.select_head or bone.select:
                points.append(bone.head)
            if bone.select_tail or bone.select:
                points.append(bone.tail)

        if not points:
            return None

        local_median = sum(points, mathutils.Vector()) / len(points)
        return obj.matrix_world @ local_median

    if obj.mode == "POSE" and obj.type == "ARMATURE":
        selected_pose_bones = context.selected_pose_bones
        if not selected_pose_bones:
            return None

        local_median = sum((b.head for b in selected_pose_bones), mathutils.Vector()) / len(selected_pose_bones)
        return obj.matrix_world @ local_median

    # If in Object Mode, get the median of selected objects' world positions
    selected_objs = context.selected_objects
    if not selected_objs:
        return None

    # Calculate median
    return sum((o.matrix_world.translation for o in selected_objs), mathutils.Vector()) / len(selected_objs)

def _get_mesh_element_counts(context: bpy.types.Context):
    """Returns vert, edge, and face count for the selected mesh."""

    # Get active selected object
    obj: bpy.types.Object = context.active_object
    if obj is None or obj.mode != "EDIT" or obj.type != "MESH":
        return None

    # Get vert, edge, and face count
    bm: bmesh.types.BMesh = bmesh.from_edit_mesh(obj.data)
    return (len(bm.verts), len(bm.edges), len(bm.faces))

def _extract_properties(props_struct: bpy.types.PropertyGroup) -> dict:
    """Extract properties and values from operators and their nested operators for easier reading."""

    # Iterate trhough 
    result = {}
    for prop in props_struct.bl_rna.properties:
        identifier = prop.identifier

        # Skip meta property
        if identifier == "rna_type":
            continue

        # Get the attribute value from the props struct
        value = getattr(props_struct, identifier)

        # Recursively extract properties from child operators
        if prop.type == "POINTER":
            if "_OT_" in identifier and isinstance(value, bpy.types.bpy_struct):
                result[identifier] = _extract_properties(value)

            continue

        # Convert vectors to tuples
        if isinstance(value, (mathutils.Vector, mathutils.Euler, mathutils.Color)):
            result[identifier] = tuple(value)

        # Try to convert the len property to a tuple if it contains more than one value
        elif hasattr(value, "__len__") and not isinstance(value, str):
            try:
                result[identifier] = tuple(value)
            except TypeError:
                result[identifier] = value

        # Otherwise, just get the value
        else:
            result[identifier] = value

    return result

def _signature_for(op) -> tuple:
    """Hacky check result to see whether the same operation was run as a result of the modify panel."""

    return (op.bl_idname, repr(_extract_properties(op.properties)))

def get_last_redo_panel_adjustment_time() -> float:
    """Returns the time of the last detected in-place redo-panel edit."""

    return _last_redo_panel_adjustment_time

def _poll() -> float:
    """Poll bpy.context.window_manager.operators to get the last action performed by the user. Returns the interval."""

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
        # Get median and mesh counts
        current_median = _get_selection_median(bpy.context)
        current_mesh_counts = _get_mesh_element_counts(bpy.context)

        # Get the new operations
        new_ops = ops[_last_op_count:current_count]

        # Create extra info block dict
        extra = {}

        # Try to get the selection delta
        if _last_median is not None and current_median is not None:
            extra["selection_delta"] = (current_median - _last_median).length

        # Check to see if the vert/edge/face count deltas returned any changes
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

            # Draft event
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

    # Check if the top entry was edited with the modify panel
    elif current_count > 0:
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
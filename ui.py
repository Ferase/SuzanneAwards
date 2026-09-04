import os

import bpy
import bpy.utils.previews

from . import manager
from . import exp
from . import daily
from . import toast
from . import sound
from .achievements._base import AchievementKind

ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")

ICON_FILES = {
    "unlocked": os.path.join(ASSETS_DIR, "img", "default", "award.png"),
    "locked": os.path.join(ASSETS_DIR, "img", "default", "locked_award.png"),
}

# Rank flavor text
RANK_FLAVOR_TEXT: dict[int, str] = {
    0: "Vert",
    10: "Edge",
    20: "Plane",
    30: "Circle",
    40: "Cube",
    80: "Cone",
    70: "Cylinder",
    60: "Ico Sphere",
    50: "UV Sphere",
    90: "Torus",
    100: "Suzanne",
}

# bpy.utils.previews.ImagePreviewCollection, populated by _load_icons()
_icons = None



def _load_icons() -> None:
    """Load and cache achievement icons."""

    global _icons

    pcoll = bpy.utils.previews.new()

    for key, path in ICON_FILES.items():
        
        if not os.path.exists(path):
            print(f"[UI] Icon not found at {path}, falling back to a builtin icon for '{key}'.")
            continue
        
        pcoll.load(key, path, "IMAGE")

    _icons = pcoll

def _icon_kwargs_for(instance) -> dict:
    """Returns the right kwarg (icon_value=... or icon=...) for a template_icon/label call."""

    key = "unlocked" if instance.unlocked else "locked"

    if _icons is not None and key in _icons:
        return {"icon_value": _icons[key].icon_id}

    return {"icon": "CHECKMARK" if instance.unlocked else "LOCKED"}

def _draw_achievement_box(layout, instance) -> None:
    """Draw one achievement's box - shared by both the Daily and Global sections."""

    box = layout.box()
    row = box.row()

    icon_col = row.column()
    icon_kwargs = _icon_kwargs_for(instance)
    if "icon_value" in icon_kwargs:
        icon_col.template_icon(scale=3.0, **icon_kwargs)
    else:
        icon_col.label(**icon_kwargs)

    text_col = row.column()
    text_col.label(text=instance.NAME)
    text_col.label(text=instance.DESC)

    status = instance.status_text()
    if status:
        text_col.label(text=status)


def _draw_daily_complete_popup(self, context: bpy.types.Context) -> None:
    """Body of the popup shown once all of today's daily achievements are complete."""

    layout = self.layout
    layout.label(text="You've completed all of today's Daily Awards!")
    layout.label(
        text=f"You can now claim a permanent boost! Future daily EXP goes from x{exp.daily_boost_multiplier} to x{exp.daily_boost_multiplier + 1}."
    )

    row = layout.row(align=True)
    row.operator("suzanneawards.skip_boost", text="Skip for now")
    row.operator("suzanneawards.powerup", text="Gimme a boost!")

def _show_daily_complete_popup() -> None:
    """Calls the daily awards complete popup."""

    bpy.context.window_manager.popup_menu(
        _draw_daily_complete_popup,
        title="All Daily Awards Complete!",
        icon="FUND",
    )

def _on_daily_complete() -> None:
    """Fires when all daily achievements are complete."""

    bpy.app.timers.register(_show_daily_complete_popup, first_interval=0.0, persistent=True)

def _add_debug_controls(layout: bpy.types.UILayout) -> None:
    """(DEBUG) Adds debug options to the N-panel view."""

    debug_header, debug_body = layout.panel("suzanne_awards_debug", default_closed=False)
    debug_header.label(text="Debug controls")

    column_btn: bpy.types.UILayout = layout.column()

    btn_unlockall: bpy.types.OperatorProperties = column_btn.operator("suzanneawards.unlockall", text="Unlock all awards")
    btn_lockall: bpy.types.OperatorProperties = column_btn.operator("suzanneawards.lockall", text="Lock all awards")
    column_btn.separator()
    btn_unlockglobal: bpy.types.OperatorProperties = column_btn.operator("suzanneawards.unlockglobal", text="Unlock global awards")
    btn_lockglobal: bpy.types.OperatorProperties = column_btn.operator("suzanneawards.lockglobal", text="Lock global awards")
    column_btn.separator()
    btn_unlockdaily: bpy.types.OperatorProperties = column_btn.operator("suzanneawards.unlockdaily", text="Unlock daily awards")
    btn_lockdaily: bpy.types.OperatorProperties = column_btn.operator("suzanneawards.lockdaily", text="Lock daily awards")

def _get_rank_text() -> str:
    level: int = exp.level

    chosen: str = ""
    for minimum_level, text in RANK_FLAVOR_TEXT.items():
        if level < minimum_level:
            break

        chosen = text

    return chosen



class SUZANNEAWARDS_OT_unlockall(bpy.types.Operator):
    bl_idname = "suzanneawards.unlockall"
    bl_label = "Unlock all achievements"
    bl_description = "Unlocks everything"

    def execute(self, context: bpy.types.Context):
        manager.set_unlocked_all(True)
        return {'FINISHED'}
    
class SUZANNEAWARDS_OT_lockall(bpy.types.Operator):
    bl_idname = "suzanneawards.lockall"
    bl_label = "Lock all achievements"
    bl_description = "Locks everything"

    def execute(self, context: bpy.types.Context):
        manager.set_unlocked_all(False)
        return {'FINISHED'}

class SUZANNEAWARDS_OT_unlockglobal(bpy.types.Operator):
    bl_idname = "suzanneawards.unlockglobal"
    bl_label = "Unlock all global achievements"
    bl_description = "Unlocks all global achievements"

    def execute(self, context: bpy.types.Context):
        manager.set_unlocked_global(True)
        return {'FINISHED'}
    
class SUZANNEAWARDS_OT_lockglobal(bpy.types.Operator):
    bl_idname = "suzanneawards.lockglobal"
    bl_label = "Lock all global achievements"
    bl_description = "Locks all global achievements"

    def execute(self, context: bpy.types.Context):
        manager.set_unlocked_global(False)
        return {'FINISHED'}

class SUZANNEAWARDS_OT_unlockdaily(bpy.types.Operator):
    bl_idname = "suzanneawards.unlockdaily"
    bl_label = "Unlock all active daily achievements"
    bl_description = "Unlocks all active daily achivements"

    def execute(self, context: bpy.types.Context):
        manager.set_unlocked_daily(True)
        return {'FINISHED'}
    
class SUZANNEAWARDS_OT_lockdaily(bpy.types.Operator):
    bl_idname = "suzanneawards.lockdaily"
    bl_label = "Lock all active daily achievements"
    bl_description = "Locks all active daily achivements"

    def execute(self, context: bpy.types.Context):
        manager.set_unlocked_daily(False)
        return {'FINISHED'}

    

class SUZANNEAWARDS_OT_skip_boost(bpy.types.Operator):
    bl_idname = "suzanneawards.skip_boost"
    bl_label = "Skip for now"
    bl_description = "Dismiss this - you can still claim your Daily Boost later today from the Achievements panel."

    def execute(self, context: bpy.types.Context):
        # Deliberately does nothing - daily.boost_available stays True,
        # so the N-panel button remains enabled for the rest of the day
        return {'FINISHED'}



class SUZANNEAWARDS_OT_boostbtn(bpy.types.Operator):
    bl_idname = "suzanneawards.powerup"
    bl_label = "Daily Boost"
    bl_description = "Every day you earn all of your daily achievements, you can click this button, allowing you to boost EXP gained from daily achievements by 2x!\n\nThis has no cap, so continuing to complete your daily achievements every day will allow you to increase it to 3x, 4x, and so on!"

    def execute(self, context: bpy.types.Context):
        claimed = daily.claim_boost()

        if claimed:
            toast.show_toast("You boosted your EXP gain!", f"Boosted x{exp.daily_boost_multiplier}")
            sound.play_boost_sound()

        # Redraw immediately so the button reflects boost_available's state
        for window in context.window_manager.windows:
            for area in window.screen.areas:
                area.tag_redraw()

        return {'FINISHED'}



class SUZANNEAWARDS_PT_panel(bpy.types.Panel):
    bl_label = "Achievements"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Achievements"

    def draw(self, context: bpy.types.Context):
        """Draw the N-panel tab."""

        layout = self.layout

        # EXP/level header
        threshold = exp.exp_required_for_level(exp.level)
        header = layout.box()
        header.label(text=f"Level {exp.level}")
        header.label(text=f"Your current rank is: {_get_rank_text()}")
        header.progress(
            factor=exp.get_progress_fraction(),
            text=f"{exp.exp}/{threshold}",
        )

        header.separator()

        header.label(text=f"Current Multiplier: x{exp.daily_boost_multiplier}")
        row_btn: bpy.types.UILayout = header.row()
        row_btn.enabled = daily.boost_available

        btn_boost: bpy.types.OperatorProperties = row_btn.operator("suzanneawards.powerup", text="Gimme a boost!")

        # Split achievement instances into their repsective types
        instances = manager.get_instances().values()
        daily_instances = [i for i in instances if getattr(i, "KIND", None) == AchievementKind.DAILY]
        global_instances = [i for i in instances if getattr(i, "KIND", None) == AchievementKind.GLOBAL]

        if manager.DEBUG:
            _add_debug_controls(layout)

        # Collapsable section for daily achievements
        daily_header, daily_body = layout.panel("suzanne_awards_daily", default_closed=False)
        daily_header.label(text="Daily Awards")
        if daily_body is not None:
            for instance in daily_instances:
                _draw_achievement_box(daily_body, instance)

        # Collapsable section for global achievements
        global_header, global_body = layout.panel("suzanne_awards_global", default_closed=False)
        global_header.label(text="Global Awards")
        if global_body is not None:
            for instance in global_instances:
                _draw_achievement_box(global_body, instance)



classes = (
    SUZANNEAWARDS_OT_boostbtn,
    SUZANNEAWARDS_OT_skip_boost,
    SUZANNEAWARDS_PT_panel
)

debug_classes = (
    SUZANNEAWARDS_OT_unlockall,
    SUZANNEAWARDS_OT_lockall,
    SUZANNEAWARDS_OT_unlockglobal,
    SUZANNEAWARDS_OT_lockglobal,
    SUZANNEAWARDS_OT_unlockdaily,
    SUZANNEAWARDS_OT_lockdaily
)



def register():
    """Register the N-panel."""

    if manager.DEBUG:
        for cls in debug_classes:
            bpy.utils.register_class(cls)

    for cls in classes:
        bpy.utils.register_class(cls)

    # Deferred - see _load_icons() docstring
    bpy.app.timers.register(_load_icons, first_interval=0.0, persistent=True)

    daily.add_daily_complete_listener(_on_daily_complete)

def unregister():
    """Unregister the N-panel."""

    if manager.DEBUG:
        for cls in reversed(debug_classes):
            bpy.utils.unregister_class(cls)

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    if bpy.app.timers.is_registered(_load_icons):
        bpy.app.timers.unregister(_load_icons)

    try:
        if _icons is not None:
            bpy.utils.previews.remove(_icons)
            _icons = None
    except UnboundLocalError:
        pass
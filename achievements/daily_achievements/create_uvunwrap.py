from .._base import DailyAchievement
from ...events import AchievementEvent
import bpy
import bmesh



class CreateUVUnwrap(DailyAchievement):
    ID = "daily_create_uvunwrap"
    NAME = "3D 2 2D"
    DESC = "UV unwrap some mesh"
    EXP = 5
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [1, 2, 5]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = 0

        # Placeholder
        self.goal = self.GOAL_VARIANTS[0]

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        if event.bl_idname != "UV_OT_unwrap":
            return

        obj: bpy.types.Object = bpy.context.active_object
        if not obj:
            return

        bm: bmesh.types.BMesh = bmesh.from_edit_mesh(obj.data)
        if not bm.verts:
            return

        self.count += 1
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"

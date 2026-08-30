from .._base import DailyAchievement
from ...events import AchievementEvent
import bpy
import bmesh



class CreateFaces(DailyAchievement):
    ID = "daily_create_faces"
    NAME = "Patch It Up!"
    DESC = "Fill in holes with faces on meshes"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [25, 50, 100]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = 0
        self.valid_ops: list[str] = [
            "MESH_OT_fill",
            "MESH_OT_fill_grid",
            "MESH_OT_edge_face_add",
            "MESH_OT_bridge_edge_loops"
        ]

        # Placeholder
        self.goal = self.GOAL_VARIANTS[0]

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        if event.bl_idname not in self.valid_ops:
            return

        obj: bpy.types.Object = bpy.context.active_object
        if not obj or obj.type != "MESH":
            return

        selected_face_count: int = obj.data.total_face_sel
        if selected_face_count <= 0:
            return

        self.count += selected_face_count
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"

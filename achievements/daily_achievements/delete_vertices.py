from .._base import DailyAchievement
from ...events import AchievementEvent



class DeleteVertices(DailyAchievement):
    ID = "daily_delete_vertices"
    NAME = "Break It Down"
    DESC = "Delete or dissolve vertices on meshes"
    EXP = 5
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [25, 50, 100]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = 0
        self.valid_ops: list[str] = [
            "MESH_OT_delete",
            "MESH_OT_dissolve_verts"
        ]

        # Placeholder
        self.goal = self.GOAL_VARIANTS[0]

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        if event.bl_idname not in self.valid_ops:
            return

        # if event.bl_idname == "MESH_OT_delete":
        #     deleted_type: str = event.properties.get("type", "")
        #     if not deleted_type or deleted_type != "VERT":
        #         return

        deleted_vert_count: int = abs(event.extra.get("vert_count_delta", 0))
        if deleted_vert_count == 0:
            return

        self.count += deleted_vert_count
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"

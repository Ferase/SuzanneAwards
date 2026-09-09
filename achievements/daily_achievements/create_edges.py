from .._base import DailyAchievement
from ...events import AchievementEvent


class CreateEdges(DailyAchievement):
    ID = "daily_create_edges"
    NAME = "Connect the Dots"
    DESC = "Create edges"
    EXP = 5
    TRACKED_FIELDS = ["count"]
    INIT_VALUE: int = 0

    GOAL_VARIANTS = [25, 50, 100]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = self.INIT_VALUE
        self.valid_ops: list[str] = [
            "MESH_OT_extrude_region_move",
            "MESH_OT_extrude_edges_move",
            "MESH_OT_edge_face_add",
            "MESH_OT_bridge_edge_loops",
        ]

        self.goal = self.GOAL_VARIANTS[0]

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        if event.bl_idname not in self.valid_ops:
            return

        edge_delta = event.extra.get("edge_count_delta", 0)
        if edge_delta <= 0:
            return

        self.count += edge_delta
        if self.count < self.goal:
            self.save()
            return
        
        self.unlock()

    def status_text(self) -> str:
        return f"{self.count:,}/{self.goal:,}"

    def get_progress_fraction(self):
        return self.count / self.goal if self.goal > 0 else 0.0
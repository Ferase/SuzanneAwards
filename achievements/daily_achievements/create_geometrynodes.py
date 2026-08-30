from .._base import DailyAchievement
from ...events import AchievementEvent



class CreateGeometryNodes(DailyAchievement):
    ID = "daily_create_geometrynodes"
    NAME = "Procedural Modelling"
    DESC = "Create Geometry Nodes groups on objects"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [5, 10]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = 0

        # Placeholder
        self.goal = self.GOAL_VARIANTS[0]

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        if event.bl_idname != "NODE_OT_new_geometry_node_group_assign":
            return

        self.count += 1
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"

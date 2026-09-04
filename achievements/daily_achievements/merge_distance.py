from .._base import DailyAchievement
from ...events import AchievementEvent



class MergeDistance(DailyAchievement):
    ID = "daily_merge_distance"
    NAME = "Sewing"
    DESC = "Merge disconnected meshes by distance in Edit Mode"
    EXP = 5
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [10, 15, 20]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = 0

        # Placeholder
        self.goal = self.GOAL_VARIANTS[0]

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        if event.bl_idname != "MESH_OT_remove_doubles":
            return

        any_change: bool = any([
            event.extra.get("vert_count_delta", 0),
            event.extra.get("edge_count_delta", 0),
            event.extra.get("face_count_delta", 0)
        ])

        if not any_change:
            return

        self.count += 1
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"

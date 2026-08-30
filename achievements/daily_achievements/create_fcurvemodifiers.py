from .._base import DailyAchievement
from ...events import AchievementEvent



class CreateFCurveModifiers(DailyAchievement):
    ID = "daily_create_fcurvemodifiers"
    NAME = "Add It To the Mix"
    DESC = "Add F-curve modifiers to animated objects' transforms or attributes"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [1, 2, 5, 10]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = 0

        # Placeholder
        self.goal = self.GOAL_VARIANTS[0]

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        if event.bl_idname != "GRAPH_OT_fmodifier_add":
            return

        self.count += 1
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"

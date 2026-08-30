from .._base import DailyAchievement
from ...events import AchievementEvent



class DoOperations(DailyAchievement):
    ID = "daily_do_operations"
    NAME = "Anything Goes"
    DESC = "Perform general actions"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [50, 100, 200]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = 0

        # Placeholder
        self.goal = self.GOAL_VARIANTS[0]

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        self.count += 1
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"

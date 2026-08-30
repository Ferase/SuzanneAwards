from .._base import DailyAchievement
from ...events import AchievementEvent



class RenderComposite(DailyAchievement):
    ID = "daily_render_composite"
    NAME = "Final Pass"
    DESC = "Run the compositor on rendered images and frames"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [25, 50, 100]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = 0

        # Placeholder
        self.goal = self.GOAL_VARIANTS[0]

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "composite_complete":
            return

        self.count += 1
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"

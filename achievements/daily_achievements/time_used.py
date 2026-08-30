from .._base import DailyAchievement
from ...events import AchievementEvent
from ... import daily



class TimeUsed(DailyAchievement):
    ID = "daily_time_used"
    NAME = "Blender Time!"
    DESC = "Use Blender for {goal_label}"
    EXP = 40

    GOAL_VARIANTS = [
        (3600, "1 hour"),
        (7200, "2 hours"),
        (10800, "3 hours"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self.goal = self.GOAL_VARIANTS[0]

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "playtime":
            return

        if event.extra.get("daily_seconds", 0) >= self.goal:
            self.unlock()

    def status_text(self) -> str:
        current_hours = daily.get_daily_seconds() / 3600.0
        goal_hours = self.goal / 3600.0
        return f"{min(current_hours, goal_hours):.1f}h/{goal_hours:.1f}h"
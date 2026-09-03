from .._base import GlobalAchievement
from ...events import AchievementEvent
from ... import playtime



class TimeUsed10H(GlobalAchievement):
    ID = "global_time_used_10h"
    NAME = "So It Begins"
    DESC = "Use Blender for a cumulative total of 10 hours"
    EXP = 200

    def __init__(self) -> None:
        super().__init__()
        self.goal = self._seconds_from_hours(10)

    def _seconds_from_hours(self, hours: int) -> int:
        return hours * 3600

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "playtime":
            return

        if event.extra.get("total_seconds", 0) >= self.goal:
            self.unlock()

    def status_text(self) -> str:
        current_hours = playtime.total_seconds / 3600.0
        goal_hours = self.goal / 3600.0
        return f"{min(current_hours, goal_hours):.1f}h/{goal_hours:.1f}h"
from .._base import GlobalAchievement
from ...events import AchievementEvent
from ... import playtime



class Startup2D(GlobalAchievement):
    ID = "global_startup_2d"
    NAME = "Back Again"
    DESC = "Open Blender on 2 consecutive days"
    EXP = 25

    def __init__(self) -> None:
        super().__init__()
        self.goal = 2

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "startup":
            return

        if event.extra.get("streak", 0) >= self.goal:
            self.unlock()

    def status_text(self) -> str:
        progress: int = min(playtime.get_current_streak(), self.goal)
        progress_days_text: str = "day" if progress == 1 else "days"
        goal_days_text: str = "day" if self.goal == 1 else "days"
        return f"{progress} {progress_days_text}/{self.goal} {goal_days_text}"
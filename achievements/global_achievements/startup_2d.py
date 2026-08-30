from .._base import GlobalAchievement
from ...events import AchievementEvent
from ... import playtime


class Startup2D(GlobalAchievement):
    ID = "global_startup_2d"
    NAME = "Back Again"
    DESC = "Open Blender on 2 consecutive days"
    EXP = 25

    # No TRACKED_FIELDS - playtime.py is the single source of truth for
    # the streak, not this instance. Storing our own copy would go
    # stale the moment this achievement unlocks (see status_text()).

    def __init__(self) -> None:
        super().__init__()
        self.goal = 2

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "startup":
            return

        if event.extra["streak"] >= self.goal:
            self.unlock()

    def status_text(self) -> str:
        # Read the LIVE streak directly, not a cached value. Once
        # unlocked, this achievement stops receiving "login" events
        # entirely (manager.handle_event() skips unlocked instances),
        # so anything stored on self would freeze at whatever the
        # streak was at the moment of unlock - this way the N-panel
        # always shows the true current streak, locked or not.
        progress: int = min(playtime.get_current_streak(), self.goal)
        progress_days_text: str = "day" if progress == 1 else "days"
        goal_days_text: str = "day" if self.goal == 1 else "days"
        return f"{progress} {progress_days_text}/{self.goal} {goal_days_text}"
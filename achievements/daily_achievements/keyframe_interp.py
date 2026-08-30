from .._base import DailyAchievement
from ...events import AchievementEvent



class KeyframeInterp(DailyAchievement):
    ID = "daily_keyframe_interp"
    NAME = "That Feels Right"
    DESC = "Modify the interpolation type of keyframes"
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

        if event.bl_idname != "ACTION_OT_interpolation_type":
            return

        self.count += 1
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"

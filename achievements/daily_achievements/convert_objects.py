from .._base import DailyAchievement
from ...events import AchievementEvent



class ConvertObjects(DailyAchievement):
    ID = "daily_convert_objects"
    NAME = "Metamorphosis"
    DESC = "Convert objects to another type"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [1, 2, 5]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = 0

        # Placeholder
        self.goal = self.GOAL_VARIANTS[0]

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        if event.bl_idname != "OBJECT_OT_convert":
            return

        self.count += 1
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"

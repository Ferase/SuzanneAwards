from .._base import DailyAchievement
from ...events import AchievementEvent



class CreateModifiers(DailyAchievement):
    ID = "daily_create_amodifiers"
    NAME = "Nondestructive Modelling"
    DESC = "Add modifiers to objects"
    EXP = 30
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

        if event.bl_idname != "OBJECT_OT_modifier_add":
            return

        self.count += 1
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"

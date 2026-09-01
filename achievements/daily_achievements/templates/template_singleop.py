"""Defines a simple template for achievements that just check that the suer has performed an operator operation and that it matches exactly one specific operation."""



from ..._base import DailyAchievement
from ....events import AchievementEvent



class TemplateSingleOpAchievement(DailyAchievement):
    ID = "daily_tempalte_singelop"
    NAME = "[TEMPALTE] Single Operator"
    DESC = "A reusable template for single operator achievements."
    EXP = 0
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [0, 0, 0]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = 0
        self.desired_op: str = "operator_id_here"

        # Placeholder
        self.goal = self.GOAL_VARIANTS[0]

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        if event.bl_idname != self.desired_op:
            return

        self.count += 1
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"

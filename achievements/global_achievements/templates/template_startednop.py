"""Defines a simple template that checks if the operator's ID begins and ends with the specified substrings. If one is nnot specified, it will only check if it begins with something or ends with something depending on what the user has given."""



from ..._base import GlobalAchievement
from ....events import AchievementEvent



class TempalteStartEndOpAchievement(GlobalAchievement):
    ID = "daily_tempalte_startsendsop"
    NAME = "[TEMPALTE] Starts with/ends with Operator"
    DESC = "A reusable template for achievements that are seeking operators that start and end with something."
    EXP = 0
    TRACKED_FIELDS = ["count"]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = 0

        self._ignore: str = "__IgNoRe__"
        self.op_startswith: str = self._ignore
        self.op_endswith: str = self._ignore

        self.goal = 0

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        if self.op_startswith == self._ignore and self.op_endswith == self._ignore:
            print("[TempalteStartEndOpAchievement] No startswith or endswith overrides were given!")
            return

        if not event.bl_idname.startswith(self.op_startswith) and self.op_startswith != self._ignore:
            return

        if not event.bl_idname.endswith(self.op_endswith) and self.op_endswith != self._ignore:
            return

        self.count += 1
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"

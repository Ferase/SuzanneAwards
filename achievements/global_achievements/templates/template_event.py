"""Defines a simple template for achievements that just check that an event has fired to award progress."""



from ..._base import GlobalAchievement
from ....events import AchievementEvent



class TemplateEventAchievement(GlobalAchievement):
    ID = "global_tempalte_event"
    NAME = "[TEMPALTE] Event"
    DESC = "A reusable template for achievements that ony check for a sepcific event."
    EXP = 0
    TRACKED_FIELDS = ["count"]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = 0
        self.event_id: str = "event_id_here"
        self.goal = 0

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != self.event_id:
            return

        self.count += 1
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"

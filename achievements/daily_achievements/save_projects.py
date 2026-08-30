from .._base import DailyAchievement
from ...events import AchievementEvent



class SaveProjects(DailyAchievement):
    ID = "dail_save_projects"
    NAME = "Lock It In"
    DESC = "Save projects"
    EXP = 10
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [1, 2, 5]

    def __init__(self) -> None:
        super().__init__()
        self.count = 0
        self.goal = self.GOAL_VARIANTS[0]

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "file_save":
            return
 
        # Exclude Save Copy - that's its own separate achievement track
        if event.extra.get("is_copy", False):
            return

        self.count += 1
        if self.count < self.goal:
            self.save()

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"
from .._base import DailyAchievement
from ...events import AchievementEvent



class ImportProjects(DailyAchievement):
    ID = "dail_import_projects"
    NAME = "Pulling From the Archives"
    DESC = "Apppend assets from other projects into your current project"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    def __init__(self) -> None:
        super().__init__()
        self.count = 0
        self.goal = 1

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "file_blend_import":
            return

        self.count += 1
        if self.count < self.goal:
            self.save()

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"
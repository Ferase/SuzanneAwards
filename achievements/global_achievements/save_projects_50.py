from .._base import GlobalAchievement
from ...events import AchievementEvent



class SaveProjects50(GlobalAchievement):
    ID = "global_save_projects_50"
    NAME = "My Catalogue"
    DESC = "Save unique projects"
    EXP = 125
    TRACKED_FIELDS = ["count"]
    INIT_VALUE: int = 0

    def __init__(self) -> None:
        super().__init__()
        self.count = self.INIT_VALUE
        self.goal = 250

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "file_save":
            return

        if not event.extra.get("is_new_save", False):
            return

        self.count += 1
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count:,}/{self.goal:,}"

    def get_progress_fraction(self):
        return self.count / self.goal if self.goal > 0 else 0.0
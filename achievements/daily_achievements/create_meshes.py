from .._base import DailyAchievement
from ...events import AchievementEvent



class CreateMeshes(DailyAchievement):
    ID = "daily_create_meshes"
    NAME = "Building Blocks"
    DESC = "Create mesh objects in Object Mode or Edit Mode"
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

        if not event.bl_idname.startswith("MESH_"):
            return

        if not event.bl_idname.endswith("_add"):
            return

        self.count += 1
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"

from .._base import DailyAchievement
from ...events import AchievementEvent
import bpy



class SelectObjects(DailyAchievement):
    ID = "daily_select_objects"
    NAME = "Jumping Around"
    DESC = "Select objects"
    EXP = 5
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [25, 50, 100]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = 0

        # Placeholder
        self.goal = self.GOAL_VARIANTS[0]

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        if event.bl_idname != "VIEW3D_OT_select":
            return

        if not bpy.context.selected_objects:
            return

        self.count += 1
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"

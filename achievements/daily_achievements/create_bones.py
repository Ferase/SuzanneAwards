from .._base import DailyAchievement
from ...events import AchievementEvent



class CreateBones(DailyAchievement):
    ID = "daily_create_bones"
    NAME = "It's Even More Alive!"
    DESC = "Add bones to an armature"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [10, 15, 20]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = 0
        self.valid_ops: list[str] = [
            "ARMATURE_OT_bone_primitive_add",
            "ARMATURE_OT_subdivide"
        ]

        # Placeholder
        self.goal = self.GOAL_VARIANTS[0]

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        if event.bl_idname not in self.valid_ops:
            return

        self.count += 1
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"

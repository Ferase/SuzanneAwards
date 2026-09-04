from .._base import DailyAchievement
from ...events import AchievementEvent
import bpy

class MoveFootballFields(DailyAchievement):
    ID = "daily_move_football"
    NAME = "Go Long!"
    DESC = "Move or extrude objects or bones to add up to the length of {goal_label} football fields"
    EXP = 5
    TRACKED_FIELDS = ["distance"]

    GOAL_VARIANTS = [
        (1100, "10"),
        (2750, "25"),
        (5500, "50")
    ]

    def __init__(self) -> None:
        super().__init__()
        self.distance: float = 0.0

        # Placeholder
        self.goal = self.GOAL_VARIANTS[0]

    def _get_distance(self, translation_distance: float | tuple[float, ...]) -> int:
        if isinstance(translation_distance, tuple):
            translation_distance = sum(translation_distance)

        return translation_distance

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        values: tuple
        if event.bl_idname == "TRANSFORM_OT_translate":
            values = event.properties.get("value", 0.0)
        elif event.bl_idname == "MESH_OT_extrude_region_move":
            values = event.extra.get("selection_delta", 0.0)
        else:
            return

        self.distance += abs(self._get_distance(values))
        if self.distance < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{round(self.distance)} m/{self.goal} m"

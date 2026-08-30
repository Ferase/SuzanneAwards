from .._base import DailyAchievement
from ...events import AchievementEvent
import math



class RotateCircles(DailyAchievement):
    ID = "daily_rotate_circles"
    NAME = "Dizzy Yet?"
    DESC = "Rotate objects to add up to {goal_label} full circle rotations"
    EXP = 30
    TRACKED_FIELDS = ["distance"]

    GOAL_VARIANTS = [
        (3600, "10"),
        (9000, "25"),
        (18000, "50")
    ]

    def __init__(self) -> None:
        super().__init__()
        self.distance: float = 0.0

        # Placeholder
        self.goal = self.GOAL_VARIANTS[0]

    def _get_distance(self, radians: float | tuple[float,...]) -> int:
        if isinstance(radians, tuple):
            radians: float = sum(radians)

        degrees: float = math.degrees(radians)
        return degrees

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        if event.bl_idname != "TRANSFORM_OT_rotate":
            return

        self.distance += abs(self._get_distance(event.properties.get("value", 0.0)))
        if self.distance < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{round(self.distance)}°/{self.goal}°"

from .._base import GlobalAchievement
from ...events import AchievementEvent
import bpy

class MoveWorld(GlobalAchievement):
    ID = "global_move_world"
    NAME = "Around the World"
    DESC = "Move or extrude objects or bones to add up to the circumference of earth."
    EXP = 5000
    TRACKED_FIELDS = ["distance"]

    def __init__(self) -> None:
        super().__init__()
        self.distance: float = 0.0

        # Placeholder
        self.goal = 40_075

    def _get_distance(self, translation_distance: float | tuple[float, ...]) -> int:
        if isinstance(translation_distance, tuple):
            translation_distance = sum(translation_distance)

        return translation_distance * 0.001

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
        return f"{self.distance:,.1f} km/{self.goal:,.1f} km"

    def get_progress_fraction(self):
        return self.distance / self.goal if self.goal > 0 else 0.0

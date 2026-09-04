from .._base import DailyAchievement
from ...events import AchievementEvent
from typing import Any
import bpy


class CreateLoopCuts(DailyAchievement):
    ID = "daily_create_loopcuts"
    NAME = "Chop It Up!"
    DESC = "Create loop cuts on meshes in Edit Mode"
    EXP = 5
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [25, 50, 100]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = 0

        # Placeholder
        self.goal = self.GOAL_VARIANTS[0]

    def _get_loop_cuts(self, mesh_ot_loopcut: dict[str, Any]) -> int:
        return mesh_ot_loopcut.get("number_cuts", 0)

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        cuts: int = 0
        match event.bl_idname:
            case "MESH_OT_loopcut":
                cuts = self._get_loop_cuts(event.properties)
            case "MESH_OT_loopcut_slide":
                mesh_ot_loopcut: dict[str, Any] | None = event.properties.get("MESH_OT_loopcut", None)
                if not mesh_ot_loopcut:
                    return

                cuts = cuts = self._get_loop_cuts(mesh_ot_loopcut)
            case _:
                return

        if not cuts:
            return

        self.count += cuts
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"

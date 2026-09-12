from .._base import DailyAchievement
from ...events import AchievementEvent
import bpy



class MoveGraph(DailyAchievement):
    ID = "daily_move_graph"
    NAME = "The Perfect Sweep"
    DESC = "Move, rotate, resize, and transform keyframes in the Graph Editor"
    EXP = 5
    TRACKED_FIELDS = ["count"]
    INIT_VALUE: int = 0

    GOAL_VARIANTS = [25, 50, 100]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = self.INIT_VALUE
        self.valid_ops: list[str] = [
            "TRANSFORM_OT_translate",
            "TRANSFORM_OT_rotate",
            "TRANSFORM_OT_trackball",
            "TRANSFORM_OT_resize"
        ]

        # Placeholder
        self.goal = self.GOAL_VARIANTS[0]

    def _user_in_graph_editor(self) -> bool:
        """Check if the user is in the graph editor."""
    
        wm = bpy.context.window_manager
        if wm is None:
            return False
    
        for window in wm.windows:
            for area in window.screen.areas:
                if area.type != "GRAPH_EDITOR":
                    return True
    
        return False

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        if not self._user_in_graph_editor():
            return

        if event.bl_idname not in self.valid_ops:
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

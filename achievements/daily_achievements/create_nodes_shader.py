from .._base import DailyAchievement
from ...events import AchievementEvent
import bpy



class CreateNodesShader(DailyAchievement):
    ID = "daily_create_nodes_shader"
    NAME = "Shading Pass"
    DESC = "Create, connect, or disconnect nodes in the Shader Editor"
    EXP = 5
    TRACKED_FIELDS = ["count"]
    INIT_VALUE: int = 0

    GOAL_VARIANTS = [25, 50]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = self.INIT_VALUE
        self.space_tree_type: str = "ShaderNodeTree"
        self.valid_ops: list[str] = [
            "NODE_OT_add_node",
            "NODE_OT_link",
            "NODE_OT_duplicate_move",
            "NODE_OT_translate_attach_remove_on_cancel"
        ]

        # Placeholder
        self.goal = self.GOAL_VARIANTS[0]

    def _user_in_node_editor(self) -> bool:
        """Check if the user is in the shader editor."""
    
        wm = bpy.context.window_manager
        if wm is None:
            return False
    
        for window in wm.windows:
            for area in window.screen.areas:
                if area.type != "NODE_EDITOR":
                    continue
    
                space = area.spaces.active
                if space is not None and getattr(space, "tree_type", None) == self.space_tree_type:
                    return True
    
        return False

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        if event.bl_idname not in self.valid_ops:
            return

        if not self._user_in_node_editor():
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

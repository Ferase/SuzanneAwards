from .._base import DailyAchievement
from ...events import AchievementEvent
import bpy



class CreateNodesShader(DailyAchievement):
    ID = "daily_create_nodes_shader"
    NAME = "Shading Pass"
    DESC = "Create, connect, or disconnect nodes in the Shader Editor"
    EXP = 5
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [25, 50]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = 0
        self.space_tree_type: str = "ShaderNodeTree"
        self.valid_ops: list[str] = [
            "NODE_OT_add_node",
            "NODE_OT_link",
            "NODE_OT_translate_attach_remove_on_cancel"
        ]

        # Placeholder
        self.goal = self.GOAL_VARIANTS[0]

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        if event.bl_idname not in self.valid_ops:
            return

        space: bpy.types.Space = bpy.context.space_data

        if not space or space.type != "NODE_EDITOR":
            return

        if space.tree_type != self.space_tree_type:
            return

        self.count += 1
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"

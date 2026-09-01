from .create_nodes_shader import CreateNodesShader



class CreateNodesCompositor(CreateNodesShader):
    ID = "daily_create_nodes_compositor"
    NAME = "Tuning Things Up"
    DESC = "Create, connect, or disconnect nodes in the Compositor"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [25, 50]

    def __init__(self) -> None:
        super().__init__()
        self.space_tree_type: str = "CompositorNodeTree"
        self.goal = self.GOAL_VARIANTS[0]

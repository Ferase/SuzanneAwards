from .create_nodes_shader import CreateNodesShader



class CreateNodesGeometry(CreateNodesShader):
    ID = "daily_create_nodes_geometry"
    NAME = "Whole New World"
    DESC = "Create, connect, or disconnect nodes in the Genometry Nodes Editor"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [25, 50]

    def __init__(self) -> None:
        super().__init__()
        self.space_tree_type: str = "GeometryNodeTree"

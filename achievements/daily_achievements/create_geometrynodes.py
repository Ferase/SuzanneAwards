from .templates.template_multiop import TemplateMultiOpAchievement



class CreateGeometryNodes(TemplateMultiOpAchievement):
    ID = "daily_create_geometrynodes"
    NAME = "Procedural Modelling"
    DESC = "Create Geometry Nodes groups on objects"
    EXP = 5

    GOAL_VARIANTS = [5, 10]

    def __init__(self) -> None:
        super().__init__()
        self.valid_ops: list[str] = [
            "NODE_OT_new_geometry_node_group_assign",
            "OBJECT_OT_geometry_node_tree_copy_assign",
            "NODE_OT_new_geometry_nodes_modifier"
        ]
        self.goal = self.GOAL_VARIANTS[0]

from .templates.template_singleop import TemplateSingleOpAchievement



class CreateGeometryNodes(TemplateSingleOpAchievement):
    ID = "daily_create_geometrynodes"
    NAME = "Procedural Modelling"
    DESC = "Create Geometry Nodes groups on objects"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [5, 10]

    def __init__(self) -> None:
        super().__init__()
        self.desired_op: str = "NODE_OT_new_geometry_node_group_assign"
        self.goal = self.GOAL_VARIANTS[0]

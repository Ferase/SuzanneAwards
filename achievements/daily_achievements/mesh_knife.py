from .templates.template_singleop import TemplateSingleOpAchievement



class MeshKnife(TemplateSingleOpAchievement):
    ID = "daily_mesh_knife"
    NAME = "Slice and Dice"
    DESC = "Use the knife tool on meshes in Edit Mode"
    EXP = 5
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [1, 2, 5]

    def __init__(self) -> None:
        super().__init__()
        self.desired_op: str = "MESH_OT_knife_tool"
        self.goal = self.GOAL_VARIANTS[0]
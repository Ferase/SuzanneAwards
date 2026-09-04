from .templates.template_singleop import TemplateSingleOpAchievement



class MeshBevel(TemplateSingleOpAchievement):
    ID = "daily_mesh_bevel"
    NAME = "Rounding Out"
    DESC = "Use the bevel function on meshes in Edit Mode"
    EXP = 5
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [10, 15, 25]

    def __init__(self) -> None:
        super().__init__()
        self.desired_op: str = "MESH_OT_bevel"
        self.goal = self.GOAL_VARIANTS[0]
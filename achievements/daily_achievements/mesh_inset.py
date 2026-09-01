from .templates.template_singleop import TemplateSingleOpAchievement



class MeshInset(TemplateSingleOpAchievement):
    ID = "daily_mesh_inset"
    NAME = "Junction"
    DESC = "Use the inset tool on meshes in Edit Mode"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [10, 15, 20]

    def __init__(self) -> None:
        super().__init__()
        self.desired_op: str = "MESH_OT_inset"
        self.goal = self.GOAL_VARIANTS[0]
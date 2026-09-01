from .templates.template_singleop import TemplateSingleOpAchievement



class MeshSpin(TemplateSingleOpAchievement):
    ID = "daily_mesh_spin"
    NAME = "Junction"
    DESC = "Use the spin tool on meshes in Edit Mode"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [5, 10, 15]

    def __init__(self) -> None:
        super().__init__()
        self.desired_op: str = "MESH_OT_spin"
        self.goal = self.GOAL_VARIANTS[0]
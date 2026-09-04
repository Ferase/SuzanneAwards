from .templates.template_startednop import TempalteStartEndOpAchievement



class CreateMeshes(TempalteStartEndOpAchievement):
    ID = "daily_create_meshes"
    NAME = "Building Blocks"
    DESC = "Create mesh objects in Object Mode or Edit Mode"
    EXP = 5
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [10, 15, 20]

    def __init__(self) -> None:
        super().__init__()
        self.op_startswith: str = "MESH_"
        self.op_endswith: str = "_add"

        # Placeholder
        self.goal = self.GOAL_VARIANTS[0]

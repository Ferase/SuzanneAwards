from .templates.template_startednop import TempalteStartEndOpAchievement



class CreateCurves(TempalteStartEndOpAchievement):
    ID = "daily_create_curves"
    NAME = "More Than Mesh"
    DESC = "Create curve objects in Object Mode or Edit Mode"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [10, 15, 20]

    def __init__(self) -> None:
        super().__init__()
        self.op_startswith: str = "CURVE_"
        self.op_endswith: str = "_add"

        self.goal = self.GOAL_VARIANTS[0]
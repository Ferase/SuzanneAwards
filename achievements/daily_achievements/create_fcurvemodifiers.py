from .templates.template_singleop import TemplateSingleOpAchievement



class CreateFCurveModifiers(TemplateSingleOpAchievement):
    ID = "daily_create_fcurvemodifiers"
    NAME = "Add It To the Mix"
    DESC = "Add F-curve modifiers to animated objects' transforms or attributes"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [1, 2, 5, 10]

    def __init__(self) -> None:
        super().__init__()
        self.desired_op: str = "GRAPH_OT_fmodifier_add"
        self.goal = self.GOAL_VARIANTS[0]
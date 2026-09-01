from .templates.template_singleop import TemplateSingleOpAchievement



class ConvertObjects(TemplateSingleOpAchievement):
    ID = "daily_convert_objects"
    NAME = "Metamorphosis"
    DESC = "Convert objects to another type"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [1, 2, 5]

    def __init__(self) -> None:
        super().__init__()
        self.desired_op: str = "OBJECT_OT_convert"
        self.goal = self.GOAL_VARIANTS[0]

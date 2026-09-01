from .templates.template_singleop import TemplateSingleOpAchievement



class CreateLights(TemplateSingleOpAchievement):
    ID = "daily_create_lights"
    NAME = "Shed Some Light"
    DESC = "Create light objects"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [10, 15, 20]

    def __init__(self) -> None:
        super().__init__()
        self.desired_op: str = "OBJECT_OT_light_add"
        self.goal = self.GOAL_VARIANTS[0]

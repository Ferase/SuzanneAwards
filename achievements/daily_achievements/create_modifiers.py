from .templates.template_singleop import TemplateSingleOpAchievement



class CreateModifiers(TemplateSingleOpAchievement):
    ID = "daily_create_amodifiers"
    NAME = "Nondestructive Modelling"
    DESC = "Add modifiers to objects"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [10, 15, 20]

    def __init__(self) -> None:
        super().__init__()
        self.desired_op: str = "OBJECT_OT_modifier_add"
        self.goal = self.GOAL_VARIANTS[0]

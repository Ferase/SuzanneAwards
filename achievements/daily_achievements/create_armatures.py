from .templates.template_singleop import TemplateSingleOpAchievement



class CreateArmatures(TemplateSingleOpAchievement):
    ID = "daily_create_armatures"
    NAME = "It's Alive!"
    DESC = "Create armature objects"
    EXP = 5
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [1, 2, 5]

    def __init__(self) -> None:
        super().__init__()
        self.desired_op: str = "OBJECT_OT_armature_add"
        self.goal = self.GOAL_VARIANTS[0]
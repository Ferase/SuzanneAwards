from .templates.template_singleop import TemplateSingleOpAchievement



class CreateShapeKeys(TemplateSingleOpAchievement):
    ID = "daily_create_shapekeys"
    NAME = "Fine Detail"
    DESC = "Add new shape keys to an object"
    EXP = 5
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [10, 15, 20]

    def __init__(self) -> None:
        super().__init__()
        self.desired_op: str = "OBJECT_OT_shape_key_add"
        self.goal = self.GOAL_VARIANTS[0]

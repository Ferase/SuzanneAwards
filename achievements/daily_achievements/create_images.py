from .templates.template_singleop import TemplateSingleOpAchievement



class CreateImages(TemplateSingleOpAchievement):
    ID = "daily_create_cameras"
    NAME = "Freedom of An Empty Canvas"
    DESC = "Create new images inside Blender"
    EXP = 5

    GOAL_VARIANTS = [5, 10, 15]

    def __init__(self) -> None:
        super().__init__()
        self.desired_op: str = "IMAGE_OT_new"
        self.goal = self.GOAL_VARIANTS[0]

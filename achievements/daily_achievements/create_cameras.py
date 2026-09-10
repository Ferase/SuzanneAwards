from .templates.template_singleop import TemplateSingleOpAchievement



class CreateCameras(TemplateSingleOpAchievement):
    ID = "daily_create_cameras"
    NAME = "Let's Try This Angle"
    DESC = "Create cameras"
    EXP = 5

    GOAL_VARIANTS = [10, 15, 20]

    def __init__(self) -> None:
        super().__init__()
        self.desired_op: str = "OBJECT_OT_camera_add"
        self.goal = self.GOAL_VARIANTS[0]

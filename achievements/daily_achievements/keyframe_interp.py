from .templates.template_singleop import TemplateSingleOpAchievement



class KeyframeInterp(TemplateSingleOpAchievement):
    ID = "daily_keyframe_interp"
    NAME = "That Feels Right"
    DESC = "Modify the interpolation type of keyframes"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [1, 2, 5, 10]

    def __init__(self) -> None:
        super().__init__()
        self.desired_op: str = "ACTION_OT_interpolation_type"
        self.goal = self.GOAL_VARIANTS[0]
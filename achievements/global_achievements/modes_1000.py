from .templates.template_multiop import TemplateMultiOpAchievement
from ...events import AchievementEvent



class Modes1000(TemplateMultiOpAchievement):
    ID = "global_mode_1000"
    NAME = "Seat Switcher"
    DESC = "Switch modes in the 3D View"
    EXP = 1000

    def __init__(self) -> None:
        super().__init__()
        self.valid_ops: list[str] = [
            "OBJECT_OT_editmode_toggle",
            "SCULPT_OT_sculptmode_toggle",
            "PAINT_OT_vertex_paint_toggle",
            "PAINT_OT_weight_paint_toggle",
            "PAINT_OT_texture_paint_toggle",
            "OBJECT_OT_posemode_toggle",
            "GREASE_PENCIL_OT_sculptmode_toggle",
            "GREASE_PENCIL_OT_paintmode_toggle",
            "GREASE_PENCIL_OT_weightmode_toggle",
            "GREASE_PENCIL_OT_vertexmode_toggle"
        ]

        self.goal = 1000
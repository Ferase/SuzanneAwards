from .templates.template_singleop import TemplateSingleOpAchievement



class CreateMaterials(TemplateSingleOpAchievement):
    ID = "daily_create_materials"
    NAME = "Shading Pass"
    DESC = "Create new materials"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [10, 15, 20]

    def __init__(self) -> None:
        super().__init__()
        self.desired_op: str = "MATERIAL_OT_new"
        self.goal = self.GOAL_VARIANTS[0]

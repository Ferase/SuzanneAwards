from .templates.template_multiop import TemplateMultiOpAchievement



class CreateBones(TemplateMultiOpAchievement):
    ID = "daily_create_bones"
    NAME = "It's Even More Alive!"
    DESC = "Add bones to an armature"
    EXP = 5
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [10, 15, 20]

    def __init__(self) -> None:
        super().__init__()
        self.valid_ops: list[str] = [
            "ARMATURE_OT_bone_primitive_add",
            "ARMATURE_OT_subdivide"
        ]
        
        self.goal = self.GOAL_VARIANTS[0]

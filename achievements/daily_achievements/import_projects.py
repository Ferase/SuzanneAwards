from .templates.template_event import TemplateEventAchievement



class ImportProjects(TemplateEventAchievement):
    ID = "dail_import_projects"
    NAME = "Pulling From the Archives"
    DESC = "Apppend assets from other projects into your current project"
    EXP = 5
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [1, 2, 3]

    def __init__(self) -> None:
        super().__init__()
        self.event_id = "file_blend_import"
        self.goal = self.GOAL_VARIANTS[0]
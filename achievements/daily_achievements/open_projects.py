from .templates.template_event import TemplateEventAchievement



class OpenProjects(TemplateEventAchievement):
    ID = "daily_open_projects"
    NAME = "Where Were We?"
    DESC = "Open projects"
    EXP = 5
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [1, 2, 5]

    def __init__(self) -> None:
        super().__init__()
        self.event_id: str = "file_open"
        self.goal = self.GOAL_VARIANTS[0]
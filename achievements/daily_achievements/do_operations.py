from .templates.template_event import TemplateEventAchievement



class DoOperations(TemplateEventAchievement):
    ID = "daily_do_operations"
    NAME = "Anything Goes"
    DESC = "Perform general actions"
    EXP = 30
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [50, 100, 200]

    def __init__(self) -> None:
        super().__init__()
        self.event_id = "operator"
        self.goal = self.GOAL_VARIANTS[0]

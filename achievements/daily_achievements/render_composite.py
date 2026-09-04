from .templates.template_event import TemplateEventAchievement



class RenderComposite(TemplateEventAchievement):
    ID = "daily_render_composite"
    NAME = "Final Pass"
    DESC = "Run the compositor on rendered images and frames"
    EXP = 5
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [25, 50, 100]

    def __init__(self) -> None:
        super().__init__()
        self.event_id: str = "composite_complete"
        self.goal = self.GOAL_VARIANTS[0]

from .render_engine_eevee import RenderEngineEevee
from ...events import AchievementEvent



class RenderEngineCycles(RenderEngineEevee):
    ID = "daily_render_engine_cycles"
    NAME = "Slow And Steady"
    DESC = "Successfully complete render jobs with the Cycles engine"
    EXP = 5
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [1, 2, 5]

    def __init__(self) -> None:
        super().__init__()
        self.target_engline: str = "CYCLES"
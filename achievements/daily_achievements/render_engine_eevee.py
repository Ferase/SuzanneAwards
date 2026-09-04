from .._base import DailyAchievement
from ...events import AchievementEvent



class RenderEngineEevee(DailyAchievement):
    ID = "daily_render_engine_eevee"
    NAME = "Quick And Clean"
    DESC = "Successfully complete render jobs with the EEVEE engine"
    EXP = 5
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [1, 2, 5]

    def __init__(self) -> None:
        super().__init__()
        self.count = 0
        self.target_engline: str = "BLENDER_EEVEE"
        self.goal = self.GOAL_VARIANTS[0]

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "render_complete":
            return

        render_engine: str = event.extra.get("render_engine", "")
        if not render_engine or render_engine != self.target_engline:
            return

        images_rendered: int = event.extra.get("frames", 0)
        if images_rendered <= 0:
            return

        self.count += 1
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"
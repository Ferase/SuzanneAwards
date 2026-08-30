from .._base import DailyAchievement
from ...events import AchievementEvent



class RenderImages(DailyAchievement):
    ID = "daily_render_images"
    NAME = "That's a Keeper!"
    DESC = "Successfully complete image render jobs"
    EXP = 50
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [1, 2, 5]

    def __init__(self) -> None:
        super().__init__()
        self.count = 0
        self.goal = self.GOAL_VARIANTS[0]

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "render_complete":
            return

        render_format: str = event.extra.get("render_format", "")
        if not render_format or render_format == "FFMPEG":
            return

        images_rendered: int = event.extra.get("frames", 0)
        if images_rendered != 1:
            return

        self.count += 1
        if self.count < self.goal:
            self.save()

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"
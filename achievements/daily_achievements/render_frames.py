from .._base import DailyAchievement
from ...events import AchievementEvent



class RenderFrames(DailyAchievement):
    ID = "daily_render_frames"
    NAME = "As Much As It Takes"
    DESC = "Successfully render any number of images as images or movies"
    EXP = 50
    TRACKED_FIELDS = ["count"]

    GOAL_VARIANTS = [10, 25, 50]

    def __init__(self) -> None:
        super().__init__()
        self.count = 0
        self.valid_ops: list[str] = [
            "render_complete",
            "render_cancel",
        ]

        self.goal = self.GOAL_VARIANTS[0]

    def triggered(self, event: AchievementEvent) -> None:
        if event.type not in self.valid_ops:
            return

        render_format: str = event.extra.get("render_format", "")
        if not render_format:
            return
        if event.bl_idname == "render_cancel":
            if render_format and render_format == "FFMPEG":
                return
            
        images_rendered: int = event.extra.get("frames", 0)
        if images_rendered <= 0:
            return

        self.count += images_rendered
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"
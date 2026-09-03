from .._base import GlobalAchievement
from ...events import AchievementEvent



class Render10000(GlobalAchievement):
    ID = "global_render_10000"
    NAME = "Animation Portfolio"
    DESC = "Render images or movies."
    EXP = 5000
    TRACKED_FIELDS = ["count"]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = 0
        self.valid_events: list[str] = [
            "render_complete",
            "render_cancel"
        ]

        self.goal = 10_000

    def triggered(self, event: AchievementEvent) -> None:
        if event.type not in self.valid_events:
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
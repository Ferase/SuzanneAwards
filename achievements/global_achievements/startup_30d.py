from .startup_2d import Startup2D
from ...events import AchievementEvent
from ... import playtime


class Startup30D(Startup2D):
    ID = "global_startup_30d"
    NAME = "Part of the Routine"
    DESC = "Open Blender at least once a day consecutively for 1 month"
    EXP = 750

    def __init__(self) -> None:
        super().__init__()
        self.goal = 30
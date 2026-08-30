from .startup_2d import Startup2D
from ...events import AchievementEvent
from ... import playtime


class Startup60D(Startup2D):
    ID = "global_startup_60d"
    NAME = "Can't Stop, Won't Stop"
    DESC = "Open Blender at least once a day consecutively for 2 months"
    EXP = 1500

    def __init__(self) -> None:
        super().__init__()
        self.goal = 60
from .startup_2d import Startup2D
from ...events import AchievementEvent
from ... import playtime


class Startup180D(Startup2D):
    ID = "global_startup_180d"
    NAME = "Dedication"
    DESC = "Open Blender at least once a day consecutively for 6 months"
    EXP = 5000

    def __init__(self) -> None:
        super().__init__()
        self.goal = 180
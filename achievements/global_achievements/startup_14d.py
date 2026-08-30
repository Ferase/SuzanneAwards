from .startup_2d import Startup2D
from ...events import AchievementEvent
from ... import playtime


class Startup14D(Startup2D):
    ID = "global_startup_14d"
    NAME = "Locked In"
    DESC = "Open Blender at least once a day consecutively for 2 weeks"
    EXP = 250

    def __init__(self) -> None:
        super().__init__()
        self.goal = 14
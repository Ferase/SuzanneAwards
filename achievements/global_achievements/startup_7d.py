from .startup_2d import Startup2D
from ...events import AchievementEvent
from ... import playtime


class Startup7D(Startup2D):
    ID = "global_startup_7d"
    NAME = "Clocked In"
    DESC = "Open Blender at least once a day for consecutively 1 week"
    EXP = 100

    def __init__(self) -> None:
        super().__init__()
        self.goal = 7
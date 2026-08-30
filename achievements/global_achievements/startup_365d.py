from .startup_2d import Startup2D
from ...events import AchievementEvent
from ... import playtime


class Startup365D(Startup2D):
    ID = "global_startup_365d"
    NAME = "One of Many To Come"
    DESC = "Open Blender at least once a day consecutively for 1 year"
    EXP = 10_000

    def __init__(self) -> None:
        super().__init__()
        self.goal = 365
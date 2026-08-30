from .time_used_10h import TimeUsed10H



class TimeUsed1000H(TimeUsed10H):
    ID = "global_time_used_1000h"
    NAME = "Time Well Spent"
    DESC = "Use Blender for a cumulative total of 1,000 hours"
    EXP = 10_000

    def __init__(self) -> None:
        super().__init__()
        self.goal = self._seconds_from_hours(1000)
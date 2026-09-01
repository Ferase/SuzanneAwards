from .time_used_10h import TimeUsed10H



class TimeUsed24H(TimeUsed10H):
    ID = "global_time_used_24h"
    NAME = "Day in the Life"
    DESC = "Use Blender for a cumulative total of 1 day"
    EXP = 450

    def __init__(self) -> None:
        super().__init__()
        self.goal = self._seconds_from_hours(24)
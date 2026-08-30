from .time_used_10h import TimeUsed10H



class TimeUsed100H(TimeUsed10H):
    ID = "global_time_used_100h"
    NAME = "Starting to Add Up"
    DESC = "Use Blender for a cumulative total of 100 hours"
    EXP = 1000

    def __init__(self) -> None:
        super().__init__()
        self.goal = self._seconds_from_hours(100)
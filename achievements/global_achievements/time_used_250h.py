from .time_used_10h import TimeUsed10H



class TimeUsed250H(TimeUsed10H):
    ID = "global_time_used_250h"
    NAME = "Almost Half a Month"
    DESC = "Use Blender for a cumulative total of 250 hours"
    EXP = 2500

    def __init__(self) -> None:
        super().__init__()
        self.goal = self._seconds_from_hours(250)
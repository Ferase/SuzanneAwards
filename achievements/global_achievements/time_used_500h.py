from .time_used_10h import TimeUsed10H



class TimeUsed500H(TimeUsed10H):
    ID = "global_time_used_500h"
    NAME = "How Long Has It Been?"
    DESC = "Use Blender for a cumulative total of 500 hours"
    EXP = 5000

    def __init__(self) -> None:
        super().__init__()
        self.goal = self._seconds_from_hours(500)
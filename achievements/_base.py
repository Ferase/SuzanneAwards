"""
Abstract classes for achievements.

BlenderAchievement is the shared base (unchanged behavior from before -
serialization, persistence, unlock plumbing). GlobalAchievement and
DailyAchievement both subclass it and exist so achievements/global_achievements
and achievements/daily_achievements each have a distinct type to subclass,
even though the only real behavioral difference right now is that
DailyAchievement adds GOAL_VARIANTS/pick_goal() for daily goal-count
rotation. manager.py decides *when* each kind gets instantiated - the
class itself doesn't know or care which day it is.

Fields to be defined by achievements:
- ID / NAME / DESC: as before
- EXP: integer EXP awarded on unlock
- TRACKED_FIELDS: as before
- (DailyAchievement only) GOAL_VARIANTS: optional list of possible
  self.goal values, one of which is picked when the achievement is
  selected as part of a given day's rotation
"""



import random
from typing import Any, Optional



class BlenderAchievement:
    ID: str = ""
    NAME: str = ""
    DESC: str = ""
    EXP: int = 0
    TRACKED_FIELDS: list[str] = []

    def __init__(self) -> None:
        self.unlocked: bool = False
        self.goal: Any | None = None

        # Injected by manager.init_achievements()
        self._on_persist = None
        self._on_unlock = None

    def load_progress(self, saved: Optional[dict]) -> None:
        if not saved:
            return
        self.unlocked = saved.get("unlocked", self.unlocked)
        for name in self.TRACKED_FIELDS:
            if name in saved:
                setattr(self, name, saved[name])

    def to_dict(self) -> dict:
        data = {"unlocked": self.unlocked}
        for name in self.TRACKED_FIELDS:
            data[name] = getattr(self, name)
        return data

    def save(self) -> None:
        if self._on_persist:
            self._on_persist(self)

    def unlock(self) -> None:
        if self.unlocked:
            return
        self.unlocked = True
        self.save()
        if self._on_unlock:
            self._on_unlock(self)

    def triggered(self, event) -> None:
        raise NotImplementedError

    def status_text(self) -> str:
        return ""

    def get_desc(self) -> str:
        """Description shown in the N-panel. Defaults to the static DESC
        class attribute - override (or see DailyAchievement.get_desc())
        for descriptions that need to reflect a randomly-picked goal."""

        return self.DESC



class GlobalAchievement(BlenderAchievement):
    """Always active, persists until the user deliberately resets
    progress. No behavioral difference from BlenderAchievement right
    now - exists as its own type so achievements/global_achievements/
    has something distinct to subclass, and so a future "rebirth"
    feature has an obvious single place to hook into."""

    KIND: str = "global"



class DailyAchievement(BlenderAchievement):
    """Only active on days it's selected as part of the daily rotation
    (see daily.py). Progress resets when a new day rolls, but any EXP
    already earned from it stays with the user - manager.py handles
    that distinction, not this class."""

    KIND: str = "daily"

    # Optional: possible self.goal values for count-based daily
    # achievements. If set, one is picked via pick_goal() when this
    # achievement is chosen for the day.
    #
    # Each entry can be either a plain value (e.g. 100) or a
    # (value, label) tuple (e.g. (5500, "50 football fields")) when the
    # description needs to reflect the goal in a way that a raw number
    # wouldn't read well - see get_desc() below. Achievements that don't
    # need this just use plain values and never touch goal_label at all.
    GOAL_VARIANTS: list = []

    def __init__(self) -> None:
        super().__init__()
        self.goal_label: str = ""

    def pick_goal(self, rng: random.Random) -> None:
        """Called once, when this achievement is selected as part of a
        given day's rotation. Default: pick uniformly from
        GOAL_VARIANTS, unpacking a (value, label) tuple if that's what
        was given. Override for more complex variant logic (e.g.
        weighted choices, or varying something other than self.goal)."""

        if not self.GOAL_VARIANTS:
            return

        chosen = rng.choice(self.GOAL_VARIANTS)
        if isinstance(chosen, tuple):
            self.goal, self.goal_label = chosen
        else:
            self.goal = chosen

    def get_desc(self) -> None:
        """If a label was set by pick_goal(), substitute it into DESC
        wherever "{goal_label}" appears. Achievements that use plain
        (non-tuple) GOAL_VARIANTS never set goal_label, so this is a
        no-op for them - DESC is returned exactly as written."""

        if self.goal_label:
            self.DESC = self.DESC.format(goal_label=self.goal_label)
        
        return
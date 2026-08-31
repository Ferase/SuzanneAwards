"""
Abstract classes for achievements.

Fields to be defined by achievements:
- ID / NAME / DESC: as before
- EXP: integer EXP awarded on unlock
- TRACKED_FIELDS: as before
- GOAL_VARIANTS (DailyAchievement only) : optional list of possible
  self.goal values, one of which is picked when the achievement is
  selected as part of a given day's rotation
"""



import random
from typing import Any, Optional
from enum import Enum, auto



class AchievementKind(Enum):
    GLOBAL = auto()
    DAILY = auto()

class BlenderAchievement:
    # Achievement ID
    ID: str = ""

    # Achievement Name
    NAME: str = ""

    # Achievement Description
    DESC: str = ""

    # Achievement EXP to be earned
    EXP: int = 0

    # Fields to be tracked and saved
    TRACKED_FIELDS: list[str] = []

    def __init__(self) -> None:
        # Basic state data
        self.unlocked: bool = False
        self.goal: Any | None = None

        # Injected functions by manager.init_achievements()
        self._on_persist = None
        self._on_unlock = None

    def load_progress(self, saved: Optional[dict]) -> None:
        """Load the achievement's progres and assign it."""

        # If the achievement's save data doesn't exist or wasn't passed, load nothing
        if not saved:
            return

        # Get the unlocked state from progress
        self.unlocked = saved.get("unlocked", self.unlocked)

        # Set attributes based on specified TRAKCED_FIELDS
        for name in self.TRACKED_FIELDS:
            if name in saved:
                setattr(self, name, saved[name])

    def to_dict(self) -> dict:
        """Convert the achievement's unlocked state and TRACKED_FIELDS to a serializeable dict."""

        # Get unlocked state
        data = {"unlocked": self.unlocked}

        # Get TRAKCED_FIELDS
        for name in self.TRACKED_FIELDS:
            data[name] = getattr(self, name)

        return data

    def save(self) -> None:
        """Save progress for the achievement."""

        # Run the persist function passed by manager.init_achievements()
        if self._on_persist:
            self._on_persist(self)

    def unlock(self) -> None:
        """Unlocks the achievement."""

        # If the achievement is already unlocked, do nothing
        if self.unlocked:
            return

        # Set the achievement state as unlocked and save it
        self.unlocked = True
        self.save()

        # Run all arbitrary unlock functions linked to self._on_unlock
        if self._on_unlock:
            self._on_unlock(self)

    def triggered(self, event) -> None:
        """Called when a source triggers the achievement. This is where progression logic is handled."""

        raise NotImplementedError

    def status_text(self) -> str:
        """Handles how the progression for the achievement is displayed on the achievement in the N-panel menu. Any achievements that track a count will override this and pass the display format."""

        return ""

    def get_desc(self) -> str:
        """Gets the achievement's description for display in the N-panel.
        
        Used by Daily achievements to replace placeholder text in an achievement's description depending on the random goal selected. Always returns the normal description otherwise."""

        return self.DESC



class GlobalAchievement(BlenderAchievement):
    """A persistent globally-active achievement that always tracks progress and generally has long-standing goals."""

    KIND: AchievementKind = AchievementKind.GLOBAL



class DailyAchievement(BlenderAchievement):
    """A daily-dealed achievement that will be randomly selected at the start of each day for the suer to complete. Progress resets each day, but the EXP earned stays with the user. Daily achievements have simpler or generally easier goals."""

    KIND: AchievementKind = AchievementKind.DAILY

    # Possible goal variants chosen with the daily RNG system. If specified as a list of tuples, the first value is the real, tested goal and the second is a string that will replace goal_label in the description when that goal is selected
    GOAL_VARIANTS: list[tuple[Any, str] | Any] = []

    def __init__(self) -> None:
        super().__init__()

        # Placeholder for self.get_desc() to use if the user specifies GOAL_VARIANTS as a tuple, holds the vlaid string associated with the goal that will replace goal_label in the description
        self.goal_label: str = ""

    def pick_goal(self, rng: random.Random) -> None:
        """Selects a random goal with the given RNG object when anew day has rolled over."""

        # If no goal variants are present, assume the achievement defines self.goal explicitly and do nothing
        if not self.GOAL_VARIANTS:
            return

        # Pick a random goal from GOAL_VARIANTS using the RNG object
        chosen = rng.choice(self.GOAL_VARIANTS)

        # Pass values to self.goal, also handle tuples containing gaol_label strings
        if isinstance(chosen, tuple):
            self.goal, self.goal_label = chosen
        else:
            self.goal = chosen

    def get_desc(self) -> None:
        """Gets the description for the daily achievement.
        
        If GOAL_VARIANTS is a list of tuples containing the goal values and accompanying strings, comebine those strings with the description and return that instead."""

        # Format the description string by replacing the goal_label palceholder with text from the GOAL_VARIANTS resulting tuple
        if self.goal_label:
            self.DESC = self.DESC.format(goal_label=self.goal_label)
        
        return
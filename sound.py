"""
Subsystem that operates the sound cues performed by the addon.
"""



import bpy
import aud

import os

from . import manager
from .achievements._base import BlenderAchievement, AchievementKind
from . import preferences



# Path to the bundled chime, relative to this file
ASSETS_DIR: str = os.path.join(os.path.dirname(__file__), "assets")
BASE_SOUNDS_PATH: str = os.path.join(ASSETS_DIR, "wav")
DEFAULT_SOUNDS_PATH: str = os.path.join(BASE_SOUNDS_PATH, "default")

DEFAULT_SOUND_UNLOCK_DAILY: str = os.path.join(DEFAULT_SOUNDS_PATH, "unlock_daily.wav")
DEFAULT_SOUND_UNLOCK_GLOBAL: str = os.path.join(DEFAULT_SOUNDS_PATH, "unlock_global.wav")
DEFAULT_SOUND_LEVELUP: str = os.path.join(DEFAULT_SOUNDS_PATH, "level_up.wav")
DEFAULT_SOUND_BOOST: str = os.path.join(DEFAULT_SOUNDS_PATH, "boost.wav")

# Playback device, created lazily on first use
_device = None



def _get_device() -> None:
    """Create and return the aud playback device. Only runs once."""

    # Get the global device
    global _device

    # Start the aud.Device()
    if _device is None:
        _device = aud.Device()

    return _device

def _play_sound(path: str) -> None:
    # Load the sound
    sound = aud.Sound(path)

    # Play through the device
    handle = _get_device().play(sound)

    # Set the volume
    handle.volume = preferences.get_prefs().volume

def play_unlock_sound(achievement_id: str = "", achievement_kind: AchievementKind = AchievementKind.GLOBAL, current_level: int = 0, levels_gained: int = 0) -> None:
    """Plays the achievement unlock sound. If a custom unlock sound exists, play that instead."""

    # Check if the achievement has a custom unlock sound
    path: str = DEFAULT_SOUND_UNLOCK_GLOBAL
    if achievement_id:
        new_path = os.path.join(BASE_SOUNDS_PATH, f"{achievement_id}.wav")
        if os.path.exists(new_path):
            path = new_path
        else:
            if achievement_kind == AchievementKind.DAILY:
                path = DEFAULT_SOUND_UNLOCK_DAILY

    # Play the sound
    _play_sound(path)

    if levels_gained:
        bpy.app.timers.register(lambda: play_level_up_sound(current_level, levels_gained), first_interval=2.0, persistent=True)

def play_level_up_sound(current_level: int = 1, levels_gained: int = 1) -> None:
    """Plays the level up sound."""

    # TODO: Levelling level up sounds

    # Play the sound
    _play_sound(DEFAULT_SOUND_LEVELUP)

def play_boost_sound() -> None:
    """Plays the boost sound."""

    # Play the sound
    _play_sound(DEFAULT_SOUND_BOOST)



def _on_unlock(instance: BlenderAchievement, current_level: int, levels_gained: int) -> None:
    """Plays the unlock chime, attached to the manager using manager.add_unlock_listener()."""

    play_unlock_sound(instance.ID, instance.KIND, current_level, levels_gained)

def _on_level_up(current_level: int, levels_gained: int) -> None:
    """Plays a level up chime, attached to the manager using manager.add_level_up_listener()."""

    play_level_up_sound(current_level, levels_gained)



def register():
    """Register the sound cue's unlock listener."""

    manager.add_unlock_listener(_on_unlock)

def unregister():
    """Release the playback device."""

    global _device
    _device = None

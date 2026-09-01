"""
Subsystem that operates the sound cues performed by the addon.
"""



import aud

import os

from . import manager
from .achievements._base import BlenderAchievement
from . import preferences



# Path to the bundled chime, relative to this file
ASSETS_DIR: str = os.path.join(os.path.dirname(__file__), "assets")
SOUND_PATH: str = os.path.join(ASSETS_DIR, "wav", "default", "unlock.wav")

# Playback device, created lazily on first use
_device = None



def _get_device():
    """Create and return the aud playback device. Only runs once."""

    # Get the global device
    global _device

    # Start the aud.Device()
    if _device is None:
        _device = aud.Device()

    return _device

def play_unlock_sound() -> None:
    """Plays the achievement unlock sound."""

    # Load the sound
    sound = aud.Sound(str(SOUND_PATH))

    # Play through the device
    handle = _get_device().play(sound)

    # Set the volume
    handle.volume = preferences.get_prefs().volume


def _on_unlock(instance: BlenderAchievement, levels_gained: int):
    """Plays the unlock chime, attached to the manager using manager.add_unlock_listener()."""

    play_unlock_sound()



def register():
    """Register the sound cue's unlock listener."""

    manager.add_unlock_listener(_on_unlock)

def unregister():
    """Release the playback device."""

    global _device
    _device = None

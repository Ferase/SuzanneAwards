"""
Handles storing and saving/loading achievement progress to a JSON file in Blender's config directory. All loaded states are then passed to the achievement manager for application to the achievement instances.
"""



import bpy
import json
from pathlib import Path
from typing import Any

progress: dict[str, Any] = {}
json_file_name: str = "achievement_progress.json"



def get_save_path() -> Path:
    """Returns the path of the achievement state JSON file."""

    cfg_dir = Path(bpy.utils.user_resource('CONFIG'))
    return cfg_dir / json_file_name

def load() -> None:
    """Loads achievement progress from the JSON file."""

    # Get global progress dict
    global progress

    # Get the achievement state JSON file path
    save_path: Path = get_save_path()

    # If the save doesn't exist, creeate an empty dict and move on
    if not save_path.exists():
        progress = {}
        return

    # Load the save file otherwise
    with open(save_path, "r") as f:
        progress = json.load(f)

def save() -> None:
    """Save achievement progress to the JSON file."""

    with open(get_save_path(), "w") as f:
        json.dump(progress, f, indent=2)

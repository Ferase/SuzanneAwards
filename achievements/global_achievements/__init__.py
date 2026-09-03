"""
Registry of global achievements.
"""

from .._base import GlobalAchievement

# General
from .delete_defaultcube import DeleteDefaultCube
from .recreate_defaultcube import RecreateDefaultCube
from .modes_1000 import Modes1000

# Startup Streak
from .startup_2d import Startup2D
from .startup_7d import Startup7D
from .startup_14d import Startup14D
from .startup_30d import Startup30D
from .startup_60d import Startup60D
from .startup_180d import Startup180D
from .startup_365d import Startup365D

# Object Creation
from .create_objects_1000 import CreateObjects1000

# Nodes
from .create_nodes_1000 import CreateNodes1000

# Rebder
from .render_10000 import Render10000

# Project
from .save_projects_50 import SaveProjects50
from .save_projects_100 import SaveProjects100
from .save_projects_250 import SaveProjects250
from .save_projects_500 import SaveProjects500
from .save_projects_1000 import SaveProjects1000

# Usage Time
from .time_used_10h import TimeUsed10H
from .time_used_24h import TimeUsed24H
from .time_used_100h import TimeUsed100H
from .time_used_250h import TimeUsed250H
from .time_used_500h import TimeUsed500H
from .time_used_1000h import TimeUsed1000H

GLOBAL_ACHIEVEMENT_CLASSES: list[GlobalAchievement] = [
    # General
    DeleteDefaultCube,
    RecreateDefaultCube,
    Modes1000,

    # Startup Streak
    Startup2D,
    Startup7D,
    Startup14D,
    Startup30D,
    Startup60D,
    Startup180D,
    Startup365D,

    # Object Creation
    CreateObjects1000,

    # Nodes
    CreateNodes1000,

    # Render
    Render10000,

    # Project
    SaveProjects50,
    SaveProjects100,
    SaveProjects250,
    SaveProjects500,
    SaveProjects1000,

    # Usage Time
    TimeUsed10H,
    TimeUsed24H,
    TimeUsed100H,
    TimeUsed250H,
    TimeUsed500H,
    TimeUsed1000H
]

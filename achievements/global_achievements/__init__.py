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

# Usage Time
from .time_used_10h import TimeUsed10H
from .time_used_24h import TimeUsed24H
from .time_used_100h import TimeUsed100H
from .time_used_250h import TimeUsed250H
from .time_used_500h import TimeUsed500H
from .time_used_1000h import TimeUsed1000H

# Object Creation
from .create_objects_1000 import CreateObjects1000

# Nodes
from .create_nodes_1000 import CreateNodes1000

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

    # Usage Time
    TimeUsed10H,
    TimeUsed24H,
    TimeUsed100H,
    TimeUsed250H,
    TimeUsed500H,
    TimeUsed1000H,

    # Object Creation
    CreateObjects1000,

    # Nodes
    CreateNodes1000
]

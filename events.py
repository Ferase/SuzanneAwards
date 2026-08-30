"""
An event basis, emitted from modules. All achievements take this in when emitted. Intended to be generalized and reusable.
"""



from dataclasses import dataclass, field
from typing import Any, Optional



@dataclass
class AchievementEvent:
    # Type of event
    type: str

    # bl_idname for the operator
    bl_idname: Optional[str] = None

    # RNA properties
    properties: dict = field(default_factory=dict)

    # Raw operator
    op: Any = None

    # Extra data for specific circumstances
    extra: dict = field(default_factory=dict)
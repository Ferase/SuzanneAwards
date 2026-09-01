"""
An event basis, emitted from modules. All achievements take this in when emitted. Intended to be generalized and reusable.
"""



from dataclasses import dataclass, field
from typing import Any, Optional



@dataclass
class AchievementEvent():
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

    def __post_init__(self):
        print("////////////////////")
        print("EVENT FIRED")
        print(f"\n- Type:\n  - {self.type}")
        print(f"- ID:\n  - {self.bl_idname}")

        print("- Properties")
        if not self.properties:
            print("  - None")
        else:
            for k, v in self.properties.items():
                print(f"  - {k}: {v}")

        print("- Extras")
        if not self.extra:
            print("  - None")
        else:
            for k, v in self.extra.items():
                print(f"  - {k}: {v}")
        print("////////////////////")
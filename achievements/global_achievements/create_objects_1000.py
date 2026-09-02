from .._base import GlobalAchievement
from ...events import AchievementEvent



class CreateObjects1000(GlobalAchievement):
    ID = "global_create_objects_1000"
    NAME = "That's A Lot Of Cubes"
    DESC = "Create objects in the 3D View."
    EXP = 1000
    TRACKED_FIELDS = ["count"]

    def __init__(self) -> None:
        super().__init__()
        self.count: int = 0
        self._valid_prefixes: list[str] = [
            "OBJECT_",
            "MESH_",
            "CURVE_",
            "SURFACE_"
        ]

        self.goal = 1000

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        found_prefix: bool = False
        for pfx in self._valid_prefixes:
            if event.bl_idname.startswith(pfx):
                found_prefix = True
                break

        if not found_prefix:
            return

        if not event.bl_idname.endswith("_add"):
            return

        self.count += 1
        if self.count < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{self.count}/{self.goal}"
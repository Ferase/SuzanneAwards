from .._base import GlobalAchievement
from ...events import AchievementEvent



class CreateAllMeshes(GlobalAchievement):
    ID = "global_create_all_meshes"
    NAME = "Ready Your Toolbox"
    DESC = "Create every default mesh primitive at least once"
    EXP = 25
    TRACKED_FIELDS = ["created_objects"]
    INIT_VALUE: list[str] = []

    def __init__(self) -> None:
        super().__init__()
        self.created_objects: list[str] = self.INIT_VALUE.copy()
        self._possible_objects: list[str] = [
            "MESH_OT_primitive_plane_add",
            "MESH_OT_primitive_cube_add",
            "MESH_OT_primitive_circle_add",
            "MESH_OT_primitive_uv_sphere_add",
            "MESH_OT_primitive_ico_sphere_add",
            "MESH_OT_primitive_cylinder_add",
            "MESH_OT_primitive_cone_add",
            "MESH_OT_primitive_torus_add",
            "MESH_OT_primitive_grid_add",
            "MESH_OT_primitive_monkey_add"
        ]

        self.goal = len(self._possible_objects)

    def triggered(self, event: AchievementEvent) -> None:
        if event.type != "operator":
            return

        if event.bl_idname not in self._possible_objects:
            return

        if event.bl_idname in self.created_objects:
            return

        self.created_objects.append(event.bl_idname)
        if len(self.created_objects) < self.goal:
            self.save()
            return

        self.unlock()

    def status_text(self) -> str:
        return f"{len(self.created_objects):,}/{self.goal:,}"

    def get_progress_fraction(self):
        return len(self.created_objects) / self.goal if self.goal > 0 else 0.0
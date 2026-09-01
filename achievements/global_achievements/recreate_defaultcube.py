from .._base import GlobalAchievement
from ...events import AchievementEvent
import bpy



class RecreateDefaultCube(GlobalAchievement):
    ID = "daily_recreate_defaultcube"
    NAME = "Another One, Huh?"
    DESC = "Delete the Default Cube, then immediately create a new cube"
    EXP = 15

    def __init__(self) -> None:
        super().__init__()
        self.default_cube: bpy.types.Object | None = None
        self._selected_cube: bool = False
        self._deleted: bool = False
        self._ineligable: bool = False

        self.forgivable_ops: list[str] = [
            "VIEW3D_OT_select",
            "OBJECT_OT_editmode_toggle"
        ]

        bpy.app.timers.register(self._get_default_cube, first_interval=0.5)

    def _reset(self) -> None:
        self._deleted = False
        self._selected_cube = False
        self._ineligable = False
        self._get_default_cube()

    def _get_default_cube(self) -> None:
        self.default_cube = None
        self.default_cube = bpy.data.objects.get("Cube", None)

    def _check_cube_selection(self) -> None:
        try:
            if self.default_cube.select_get():
                self._selected_cube: bool = True
                return
        except ReferenceError:
            print("[recreate_defaultcube] Default cube was destroyed, trying to find it one last time...")
            self._get_default_cube()
            self._check_cube_selection()
            return

        self._selected_cube: bool = False

    def triggered(self, event: AchievementEvent) -> None:
        if event.type == "file_new":
            bpy.app.timers.register(self._reset, first_interval=0.5, persistent=True)

        if self._ineligable:
            return

        if event.type != "operator":
            return

        if self._deleted:
            if event.bl_idname in self.forgivable_ops:
                return

            if event.bl_idname == "MESH_OT_primitive_cube_add":
                self.unlock()
                
            self._ineligable = True
            return

        if not self.default_cube:
            return

        if event.bl_idname == "OBJECT_OT_delete":
            if not self._selected_cube:
                return
            
            self._selected_cube: bool = False
            self.default_cube = None
            self._deleted = True
            return
        
        if event.bl_idname == "VIEW3D_OT_select":
            self._check_cube_selection()
            return

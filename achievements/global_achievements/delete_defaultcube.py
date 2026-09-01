from .._base import GlobalAchievement
from ...events import AchievementEvent
import bpy



class DeleteDefaultCube(GlobalAchievement):
    ID = "daily_delete_defaultcube"
    NAME = "Like Those Before You"
    DESC = "Delete the Default Cube"
    EXP = 15

    def __init__(self) -> None:
        super().__init__()
        self.default_cube: bpy.types.Object | None = None
        self._selected_cube: bool = False
        self._deleted: bool = False

        bpy.app.timers.register(self._get_default_cube, first_interval=0.5)

    def _reset(self) -> None:
        self._deleted = False
        self._selected_cube = False
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
            print("[delete_defaultcube] Default cube was destroyed, trying to find it one last time...")
            self._get_default_cube()
            self._check_cube_selection()
            return

        print("[delete_defaultcube] Default cube deselected")
        self._selected_cube: bool = False

    def triggered(self, event: AchievementEvent) -> None:
        if event.type == "file_new":
            bpy.app.timers.register(self._reset, first_interval=0.5, persistent=True)

        if self._deleted:
            return

        if not self.default_cube:
            return

        if event.type != "operator":
            return

        if event.bl_idname == "OBJECT_OT_delete":
            if not self._selected_cube:
                return
            
            self.unlock()
            self.default_cube = None
            self._selected_cube: bool = False
            self._deleted = True
            return
        
        if event.bl_idname == "VIEW3D_OT_select":
            self._check_cube_selection()
            return

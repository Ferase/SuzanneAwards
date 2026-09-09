from .create_all_meshes import CreateAllMeshes



class CreateAllCurves(CreateAllMeshes):
    ID = "global_create_all_Curves"
    NAME = "Mathematical!"
    DESC = "Create every default curve primitive at least once"
    EXP = 15
    TRACKED_FIELDS = ["created_objects"]
    INIT_VALUE: list[str] = []

    def __init__(self) -> None:
        super().__init__()
        self._possible_objects: list[str] = [
            "CURVE_OT_primitive_bezier_curve_add",
            "CURVE_OT_primitive_bezier_circle_add",
            "CURVE_OT_primitive_nurbs_curve_add",
            "CURVE_OT_primitive_nurbs_circle_add",
            "CURVE_OT_primitive_nurbs_path_add"
        ]

        self.goal = len(self._possible_objects)
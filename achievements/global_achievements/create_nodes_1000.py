from .templates.template_multiop import TemplateMultiOpAchievement



class CreateNodes1000(TemplateMultiOpAchievement):
    ID = "global_create_nodes_1000"
    NAME = "What Are These Strings?"
    DESC = "Create, connect, or disconnect nodes across all node editors"
    EXP = 1000

    def __init__(self) -> None:
        super().__init__()
        self.valid_ops: list[str] = [
            "NODE_OT_add_node",
            "NODE_OT_link",
            "NODE_OT_translate_attach_remove_on_cancel"
        ]

        self.goal = 1000

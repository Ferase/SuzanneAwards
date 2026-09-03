from .save_projects_50 import SaveProjects50



class SaveProjects1000(SaveProjects50):
    ID = "global_save_projects_1000"
    NAME = "Mountainous Catalogue"
    DESC = "Save unique projects"
    EXP = 5000

    def __init__(self) -> None:
        super().__init__()
        self.goal = 1000
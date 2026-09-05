from .save_projects_50 import SaveProjects50



class SaveProjects250(SaveProjects50):
    ID = "global_save_projects_250"
    NAME = "Mounting Catalogue"
    DESC = "Save unique projects"
    EXP = 500

    def __init__(self) -> None:
        super().__init__()
        self.goal = 250
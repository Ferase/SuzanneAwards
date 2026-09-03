from .save_projects_50 import SaveProjects50



class SaveProjects500(SaveProjects50):
    ID = "global_save_projects_500"
    NAME = "Expansive Catalogue"
    DESC = "Save unique projects"
    EXP = 2000

    def __init__(self) -> None:
        super().__init__()
        self.goal = 500
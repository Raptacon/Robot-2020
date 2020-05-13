from tkinter import (
    Tk,
    StringVar,
    Button,
    Label,
    OptionMenu
)

#from utils.reworkedConfig import FileHandler

class _Commands:
    pass

class RoboWindow(_Commands):

    def __init__(self):

        self.root = Tk()
        #config_contents = FileHandler.load(FileHandler.file_directory('window.json'))
        self._create_labels()
        self._create_runtypes()
        self._create_configs()

    def _create_labels(self):
        run_type_label = Label(self.root, text = "Run Type:")
        run_type_label.grid(row = 0, column = 0, padx = 50, pady = 50)
        run_type_label.config(font = 18)

    def _create_runtypes(self):
        OPTIONS = ["Simulation", "Deploy"]
        var = StringVar(self.root)
        var.set('Select...')

        dropdown = OptionMenu(self.root, var, *OPTIONS)
        dropdown.grid(row = 0, column = 2)
        dropdown.config(font = 18)

    def _create_versions(self):
        pass

    def _create_configs(self):
        OPTIONS = ['doof', 'minibot', 'scorpion']#[FileHandler.get_all_files('robot')]
        var = StringVar(self.root)
        var.set('Select...')

        dropdown = OptionMenu(self.root, var, *OPTIONS)
        dropdown.grid(row = 2, column = 2)
        dropdown.config(font = 18)

if __name__ == '__main__':

    robowindow = RoboWindow()
    robowindow.root.geometry("500x550")
    robowindow.root.mainloop()

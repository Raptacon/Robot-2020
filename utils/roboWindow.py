from tkinter import (
    Tk,
    StringVar,
    Button,
    Label,
    OptionMenu,
    Frame,
    messagebox
)

from os import popen as cmd
from string import ascii_letters as letters
#from utils.reworkedConfig import FileHandler

class RoboWindow:

    def __init__(self):

        self.root = Tk()
        #config_contents = FileHandler.load(FileHandler.file_directory('window.json'))
        Frame(self.root).winfo_toplevel().title("RoboWindow - Setup")
        self.root.resizable(0,0)
        self._create_labels()
        self._create_runtypes()
        self._create_configs()
        self._create_versions()
        self._create_buttons()

    def _create_labels(self):

        run_type_label = Label(self.root, text = "Run Type:", font=(None, 12))
        run_type_label.place(x = 20, y = 30)

        version_label = Label(self.root, text = "Version:", font=(None, 12))
        version_label.place(x = 20, y = 100)

        config_label = Label(self.root, text = "Configuration:", font=(None, 12))
        config_label.place(x = 20, y = 170)

    def _create_runtypes(self):
        OPTIONS = ["Simulation", "Deploy"]
        self.runtype_var = StringVar(self.root)
        self.runtype_var.set('Select...')

        dropdown = OptionMenu(self.root, self.runtype_var, *OPTIONS)
        dropdown.config(width = 15)
        dropdown.place(x = 200, y = 30)

    def _create_versions(self):
        raw_tags = cmd('git tag').readlines()

        OPTIONS = []
        for tag in raw_tags:
            OPTIONS.append(tag.rstrip('\n'))

        self.versions_var = StringVar(self.root)
        self.versions_var.set('Select...')

        dropdown = OptionMenu(self.root, self.versions_var, *OPTIONS) # Ignore this error... window works fine.
        dropdown.config(width = 15)
        dropdown.place(x = 200, y = 100)

    def _create_configs(self):
        OPTIONS = ['doof', 'minibot', 'scorpion']#[FileHandler.get_all_files('robot')]
        self.configs_var = StringVar(self.root)
        self.configs_var.set('Select...')

        dropdown = OptionMenu(self.root, self.configs_var, *OPTIONS)
        dropdown.config(width = 15)
        dropdown.place(x = 200, y = 170)

    def _create_buttons(self):

        cancel = Button(self.root, text = "Cancel", command = self.root.destroy)
        cancel.config(width = 10)
        cancel.place(x = 300, y = 510)

        continue_ = Button(self.root, text = "Continue", command = self._continue)
        continue_.config(width = 10)
        continue_.place(x = 400, y = 510)

    def _continue(self):
        dropdown_input = [
            self.runtype_var.get(),
            self.configs_var.get(),
            self.versions_var.get()
        ]

        if 'Select...' in dropdown_input:
            messagebox.showerror(title = "Invalid Choice",
                                 message = "Please select an option for every dropdown menu.")

            return

        runtype = self.runtype_var.get()
        config = self.configs_var.get()
        version = self.versions_var.get()


        if runtype == 'deploy':
            pass

if __name__ == '__main__':

    robowindow = RoboWindow()
    robowindow.root.geometry("500x550")
    robowindow.root.mainloop()

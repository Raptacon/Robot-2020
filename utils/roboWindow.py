from tkinter import (
    Tk,
    StringVar,
    Button,
    Label,
    OptionMenu,
    Frame,
    messagebox
)

import os
from os import system as cmd
from os import popen as scmd
from re import search
#from . import reworkedConfig

#TODO: Add instructions on how to use.

class RoboWindow:

    def __init__(self):

        self.root = Tk()
        #config_contents = FileHandler.load('window.json')
        self.use_recent = True # TODO: Put into config file
        Frame(self.root).winfo_toplevel().title("RoboWindow - Setup")
        self.root.resizable(0,0)
        self._create_labels()
        self._create_runtypes()
        self._create_configs()
        self._create_buttons()

    def _create_labels(self):

        intro_label = Label(self.root, text = "Robot Setup/Configuration", font = (None, 16, 'underline'))
        intro_label.place(x = 20, y = 20)

        run_type_label = Label(self.root, text = "Action:", font = (None, 12))
        run_type_label.place(x = 20, y = 90)

        config_label = Label(self.root, text = "Configuration:", font = (None, 12))
        config_label.place(x = 20, y = 140)


        most_recent_version, current_version, git_type = self._manage_versions()
        recent = f"Most recent version: {most_recent_version}"
        current = f"Currently on {git_type}: {current_version}"

        recent_label = Label(self.root, text = recent, font = (None, 10))
        recent_label.place(x = 20, y = 200)

        current_label = Label(self.root, text = current, font = (None, 10))
        current_label.place(x = 20, y = 225)

        if self.use_recent and most_recent_version != current_version:

            warning_label = Label(self.root, text = "Warning:", font = (None, 11, 'bold', 'underline'))
            warning_label.place(x = 20, y = 258)

            warning_info = Label(
                            self.root,
                            text = "Please use the most recent version by clicking below.",
                            font = (None, 10)
                            )
            warning_info.place(x = 91, y = 260)

            set_version = Button(self.root, text = "Goto Current Version", command = self._change_versions)
            set_version.config(width = 30)
            set_version.place(x = 20, y = 300)

            # info_text = ("1) Run [git status] in the commandline\n"
            #              "2) If anything is changed, do the following. Otherwise, skip to step 3.\n"
            #              "          a) Run [git stage .]\n"
            #              '          b) Run [git commit -m "temp-changes"]\n'
            #              "          c) Run [git push]\n"
            #              "3) Run [git checkout <most_recent_version_here>]\n"
            #              "4) Click 'Continue'"
            #         )

            # information = Message(self.root, text = info_text, width = 400, font = (None, 11))
            # information.place(x = 20, y = 285)

    def _change_versions(self):

        _ver, _, _ = self._manage_versions()

        cmd('git stage .')
        cmd('git commit -m "Automatic commit made by the RoboWindow"')
        cmd('git push')
        cmd('git checkout ' + _ver)

        messagebox.showinfo(title = "Success",
                            message = f"Version change successful. Now on version: {_ver}\nThe window will now reload.")

        self.root.destroy()
        self.start()

    def _create_runtypes(self):
        OPTIONS = ["Simulation", "Deploy", "Show Log"]
        self.runtype_var = StringVar(self.root)
        self.runtype_var.set('Select...')

        dropdown = OptionMenu(self.root, self.runtype_var, *OPTIONS)
        dropdown.config(width = 15)
        dropdown.place(x = 200, y = 90)

    def _create_configs(self):
        OPTIONS = ['doof.json', 'minibot.json', 'scorpion.json']#[FileHandler.get_all_files('robot', extentions = True)]
        self.configs_var = StringVar(self.root)
        self.configs_var.set('Select...')

        dropdown = OptionMenu(self.root, self.configs_var, *OPTIONS) #I
        dropdown.config(width = 15)
        dropdown.place(x = 200, y = 140)

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
            self.configs_var.get()
        ]

        action = self.runtype_var.get()
        config = self.configs_var.get()

        if 'Select...' in dropdown_input and action != 'Show Log':
            messagebox.showerror(title = "Invalid Choice",
                                 message = "Please select an option for every dropdown menu.")

            return

        recent_version, current_version, _ = self._manage_versions()

        if recent_version != current_version and self.use_recent and action != 'Show Log':
            if not (messagebox.askyesnocancel(title = "WARNING",
                                   message =
                                   "You are not running the most recent version. Are you sure you want to continue?"
                                             )):
                return

        command = f"echo {config} > RobotConfig"

        if action == 'Deploy':
            self.root.destroy()
            cmd(command)
            cmd('deploy.bat')
        elif action == 'Simulation':
            self.root.destroy()
            cmd(f'echo {config} > ..\\..\\RobotConfig')
            cmd('py robot.py sim')
        else:
            # TODO: Change when robot-logs are implemented
            self.root.destroy()
            raise NotImplementedError("Robot logs live in a different branch currently.")
            #self.root.destroy()
            #cmd(r'..\_system_utils\view_log.bat')

    def _manage_versions(self):
        tag_branch = scmd('git rev-list --tags --max-count=1').readline().strip()
        most_recent_version = scmd('git tag --contains ' + str(tag_branch)).readline().strip()

        _tag = str(scmd('git describe --tags').readline().strip())

        if search('-', _tag):
            current_version = scmd('git branch --show-current').readline().strip()
            git_type = 'branch'
        else:
            current_version = scmd('git describe --tags').readline().strip()
            git_type = 'version'

        return most_recent_version, current_version, git_type

    @staticmethod
    def start():
        """
        Starts the roboWindow.
        """

        robowindow = RoboWindow()
        robowindow.root.geometry("500x550")
        # robowindow.root.protocol("WM_DELETE_WINDOW", robowindow._revert_branch)

        icon = os.getcwd() + os.path.sep + 'utils' + os.path.sep + 'raptaconlogo_djA_icon.ico'

        robowindow.root.iconbitmap(icon)
        robowindow.root.mainloop()

if __name__ == '__main__':

    # robowindow = RoboWindow()
    # robowindow.root.geometry("500x550")
    # robowindow.root.iconbitmap('')
    # robowindow.root.mainloop()

    RoboWindow.start()

import json
import yaml
import os


# TODO disband and reallocate functions to specific modules,
#      this class if a bit much for what it does.
class FileManager:
    """
    Various helper methods for finding and loading files/folders.
    """

    @staticmethod
    def load(file_dir) -> dict:
        """
        Load a JSON or YAML file.

        :param file_dir: Directory of the JSON or YAML file
        to load. Typically should be retrieved from
        `FileManager.find_directory(name)`.
        """

        _, file_type = file_dir.split('.')

        with open(file_dir) as file:
            if file_type == '.json':
                loadedFile = json.load(file)
            elif file_type == '.yml':
                loadedFile = yaml.load(file, yaml.FullLoader)
            else:
                raise NotImplementedError(f"File type '{file_type}' is unsupported.")

        return loadedFile

    @staticmethod
    def get_all_files(folder_dir, extentions=False) -> list:
        """
        Lists the names of all the files living within a folder.
        NOTE this function automatically removes `__init__.py`
        (and all sunder/dunder files) from the list.

        :param folder_dir: Directory of the folder to use.

        :param extentions: Include extentions in file list.
        Defaults to False.

        :return: A list of all the files.
        """

        files = [f for f in os.listdir(folder_dir) if os.path.isfile(os.path.join(folder_dir, f))]
        filtered_files = []

        for file in files:
            if file.startswith('_'):
                continue
            if not extentions:
                split_file = file.split('.')
                filtered_files.append(split_file[0])
            else:
                filtered_files.append(file)

        return filtered_files

    @staticmethod
    def find_directory(name, base_dir=os.getcwd()) -> str:
        """
        Find the directory of a file or folder.

        :param name: Name of file or folder to find the directory for.
        If `name` has a period ("."), this method will assume it should
        look for a file. If not, it will assume it should look for a
        folder.

        :param base_dir: Directory to use as the root
        directory. Defaults to the current working directory (cwd).

        :return: String directory name for the file or folder.

        NOTE: This only finds the first instance
        of the directory with the specifed name.
        """

        folder = True if "." not in name else False

        if folder:
            for root, dirs, _ in os.walk(base_dir):
                if name in dirs:
                    return os.path.join(root, name)

            raise NotADirectoryError(f"Folder '{name}' doesn't exist in {base_dir}")

        else:
            for root, _, files in os.walk(base_dir):
                if name in files:
                    return os.path.join(root, name)

            raise NotADirectoryError(f"File '{name}' doesn't exist in {base_dir}")

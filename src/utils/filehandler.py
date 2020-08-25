import json
import yaml
import os

class FileHandler:
    """
    Various helper methods for finding and loading files/folders.
    """

    @staticmethod
    def load(name):
        """
        Load a .json or .yml file.
        """

        directory = FileHandler.file_directory(name)
        _, file_type = os.path.splitext(name)

        with open(directory) as file:
            if file_type == '.json':
                loadedFile = json.load(file)
            elif file_type == '.yml':
                loadedFile = yaml.load(file, yaml.FullLoader)
            else:
                raise NotImplementedError(f"File type '{file_type}' is unsupported.")

        return loadedFile

    @staticmethod
    def file_directory(name, default_path=None) -> str:
        """
        Attempt to get the directory of a requested file.
        """

        if not default_path:
            path = os.getcwd()
        else:
            path = default_path

        for root, _, files in os.walk(path):
            if name in files:
                return os.path.join(root, name)

        raise NotADirectoryError(f"File '{name}' doesn't exist in {path}")

    @staticmethod
    def folder_directory(name, default_path=None) -> str:
        """
        Attempt to get the directory of a requested folder.
        """

        if not default_path:
            path = os.getcwd()
        else:
            path = default_path

        for root, dirs, _ in os.walk(path):
            if name in dirs:
                return os.path.join(root, name)

        raise NotADirectoryError(f"Folder '{name}' doesn't exist in {path}")

    @staticmethod
    def get_all_files(foldername, extentions=False) -> list:
        """
        Lists the names of all the files living within a folder.
        NOTE this function automatically removes `__init__.py`
        from the list.
        """

        path = FileHandler.folder_directory(foldername)
        files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
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

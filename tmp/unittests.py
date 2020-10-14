import pycodestyle
import os


class TestCodeFormat:

    @property
    def all_py_files(self):
        """
        Get all python files in the cwd.
        """

        path = os.getcwd()

        test_list = []

        for root, _, files in os.walk(path):
            for filename in files:
                if not filename.startswith('.') \
                   and '.' in filename \
                   and (filename.split('.'))[1] == 'py':
                    test_list.append(os.path.join(root, filename))

        return test_list

    def test_conformance(self):
        """
        Test that we conform to PEP-8.
        """

        style = pycodestyle.StyleGuide(ignore=['E501'])
        result = style.check_files(self.all_py_files)
        tot = result.total_errors
        msg = "Urgent attention needed." if tot > 25 else "Should be observed and fixed if possible."
        print(f"Total errors/warnings: {tot}. {msg}")


if __name__ == '__main__':
    TestCodeFormat().test_conformance()

import unittest
import os
import sys
import shutil
import subprocess

"""
Integration test for file downloads.
Tests commands of the form:
   {prog} FILENAME [--append|--replace|--print]
"""


class BaseIntegrationTest(unittest.TestCase):

    def _path_in_tmpdir(self, filename):
        return self.test_dir + "/" + filename

    def _read_output(self, filename):
        """
        Returns the contents of a local file as a string.
        Strips whitespace.
        """
        f = open(self._path_in_tmpdir(filename))
        contents = f.read()
        f.close()
        return contents.strip()

    def _execute_client(self, *args):
        return subprocess.call([self.client] + list(args))

    def _execute_client_output(self, *args):
        # Command must have exit code of 0
        return subprocess.check_output([self.client] + list(args))

    def _get_dirname(self):
        """
        Temporary directory for downloaded test files.
        Implemented by subclasses.
        """
        pass

    def setUp(self):
        """
        Clears out old temporary test directories, then
        creates a new one.
        """
        # TODO - register louisrli
        self.current_dir = os.path.dirname(__file__)
        self.client = self.current_dir + "/../client.py"
        self.test_dir = self.current_dir + "/" + self._get_dirname()
        if os.path.exists(self.test_dir):
            shutil.rmtree(self.test_dir)
        os.mkdir(self.test_dir)
        os.chdir(self.test_dir)

        self.vim_str = "# test. I don't use vim."

    def doCleanups(self):
        """
        Delete the temporary test directory.
        """
        shutil.rmtree(self.test_dir)

if __name__ == 'main':
    unittest.main()

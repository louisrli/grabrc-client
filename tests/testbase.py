import unittest
import os
import shutil
import subprocess
from client import const


class BaseIntegrationTest(unittest.TestCase):

    def setUp(self):
        """
        Clears out old temporary test directories, then
        creates a new one.
        """
        self.TMPDIR = "tmp-grabrc-test"
        self.BACKUP_SUFFIX = const.Const.BACKUP_SUFFIX
        self.TEST_USER = "louisrli"
        self.script_dir = os.path.dirname(__file__)
        self.client = self.script_dir + "/../client/client.py"

        self.TEST_DIR = self.script_dir + "/" + self.TMPDIR
        if os.path.exists(self.TEST_DIR):
            shutil.rmtree(self.TEST_DIR)
        os.mkdir(self.TEST_DIR)
        os.chdir(self.TEST_DIR)

        self.__setup_config()

    def doCleanups(self):
        """
        Delete the temporary test directory.
        """
        shutil.rmtree(self.TEST_DIR)

    def __setup_config(self):
        """
        Overwrites the current configuration file with the test user
        """
        config = open(os.path.expanduser("~/.grabrc"), "w+")
        config.write(self.TEST_USER)

    # Helper functions, usable by subclasses
    def _path_in_tmpdir(self, filename):
        """Returns absolute path of a filename in the tmpdir"""
        return self.TEST_DIR + "/" + filename

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
        """ Some tests will expect failure here """
        return subprocess.call([self.client] + list(args))

    def _execute_client_output(self, *args):
        # Command must have exit code of 0
        return subprocess.check_output([self.client] + list(args))

if __name__ == 'main':
    unittest.main()

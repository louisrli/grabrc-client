import os
import unittest
from testbase import BaseIntegrationTest
from client import const

class DirectoryDownloadRepoTest(BaseIntegrationTest):

    # A list of files that are known to be in the test repository
    EXPECTED_FILES = [".vimrc", ".emacs", "test.d"]

    def test_normal(self):
        """ Tests normal and --outfile repo download """
        dir = "./foo.d"
        self._execute_client("repo", "-o %s" % dir)
        self.assertTrue(os.path.exists(dir), "New directory should be created.")
        [self.assertTrue(os.path.exists("%s/%s" % (dir, f)), "%s should be in the repo" % f)
         for f in self.EXPECTED_FILES]

    def test_existing(self):
        """Test the backup mechanism for a repo in an existing directory"""
        self._execute_client("repo")
        self._execute_client("repo")

        self.assertTrue(os.path.exists(const.Const.DEFAULT_DIRNAME), "Original repo should exist")
        self.assertTrue(os.path.exists(const.Const.DEFAULT_DIRNAME + self.BACKUP_SUFFIX),
        "Backup repo should exist.")

    def test_replace(self):
        """Test the --replace open with the repo download"""
        RAND_FILE = "randomtestfile42kmf3.test"
        RAND_PATH = os.path.join(const.Const.DEFAULT_DIRNAME, RAND_FILE)
        self._execute_client("repo")

        f = open(RAND_PATH, "w")
        f.write("foo")
        f.close()

        self._execute_client("repo", "--replace")
        self.assertFalse(os.path.exists(RAND_PATH),
            "Newly created random file should not exist after using --replace")

class DirectoryDownloadSubdirTest(BaseIntegrationTest):
    TEST_SUBDIR = "test.d"

    def test_normal(self):
        """ Test downloading a certain subdirectory of the repository """
        self._execute_client("dir:%s" % self.TEST_SUBDIR)
        self.assertTrue(os.path.exists(self.TEST_SUBDIR),
            "Subdirectory should be downloaed")

    def test_existing(self):
        self.test_normal()
        output = self._execute_client_output("dir:%s" % self.TEST_SUBDIR)
        self.assertTrue(output.find("WARNING"), "Backup should emit a warning.")
        self.assertTrue(os.path.exists(self.TEST_SUBDIR), "New directory should exist")
        self.assertTrue(os.path.exists(self.TEST_SUBDIR + self.BACKUP_SUFFIX),
            "Backup directory should exist")

    def test_destdir(self):
        new_dir = "foo"
        os.mkdir(new_dir)
        self._execute_client("dir:%s" % self.TEST_SUBDIR, "--destdir=%s" % new_dir)
        self.assertFalse(os.path.exists(self.TEST_SUBDIR),
            "Directory without --destdir should not exist.")
        self.assertEquals("f", "foo", str(os.listdir(os.path.join(new_dir, self.TEST_SUBDIR))))
        self.assertTrue(os.path.exists(os.path.join(new_dir, self.TEST_SUBDIR)),
            "Directory should be downloaded to destdir")


    def test_outfile(self):
        pass

    def test_replace(self):
        pass

    def test_nonexistent(self):
        pass


if __name__ == 'main':
    unittest.main()

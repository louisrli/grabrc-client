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
    TEST_SUBDIR = "test.d"  # The default name of the downloaded directory

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
        destdir = "foo"
        os.mkdir(destdir)

        self._execute_client("dir:%s" % self.TEST_SUBDIR, "--destdir=%s" % destdir)
        self.assertFalse(os.path.exists(self.TEST_SUBDIR),
            "Directory without --destdir should not exist.")
        self.assertEquals("f", "foo", str(os.listdir(os.path.join(destdir, self.TEST_SUBDIR))))
        self.assertTrue(os.path.exists(os.path.join(destdir, self.TEST_SUBDIR)),
            "Directory should be downloaded to destdir")


    def test_outfile(self):
        outfile = "foobar"
        self._execute_client("dir:%s" % self.TEST_SUBDIR, "--name=%s" % outfile)
        self.assertFalse(os.path.exists(self.TEST_SUBDIR),
            "Should not create a directory with the normal directory name")
        self.assertTrue(os.path.exists(outfile), "Should create dir with outfile name")
        self.assertTrue(os.path.isdir(outfile), "New file should be directory")

    def test_replace(self):
        self._execute_client("dir:%s" % self.TEST_SUBDIR)
        self._execute_client("dir:%s" % self.TEST_SUBDIR)
        self._execute_client("dir:%s" % self.TEST_SUBDIR, "--replace")

        self.assertEquals(2, len(os.listdir(os.getcwd())),
            "Two downloads + one replace should yield two files")
        self.assertTrue(os.path.isdir(self.TEST_SUBDIR),
            "Subdirectory should be downloaded and created")
        self.assertFalse(os.path.isdir(self.TEST_SUBDIR +
                                       self.BACKUP_SUFFIX + self.BACKUP_SUFFIX),
            "Second-level (.bak.bak) backup directory should not exist")

    def test_replace_nothing(self):
        """ Test the --replace flag if no directory exists yet """
        self._execute_client("dir:%s" % self.TEST_SUBDIR, "--replace")
        self.assertTrue(os.path.isdir(self.TEST_SUBDIR),
            "--replace should behave normally if no directory exists to replace.")

    def test_nonexistent(self):
        """ Test error handling when the subdirectory doesn't exist """
        self.assertTrue(self._execute_client("dir:rand1fca325hajs5had") != 0,
            "Random subdirectory should exit with nonzero value")

if __name__ == 'main':
    unittest.main()

import unittest
import os
from testbase import BaseIntegrationTest

TEST_STR = "# test. I don't use vim."
TEST_FILE = ".testrc"
RAND_FILE = ".emacs"  # Arbitrary file whose content is unimportant

# Functional test for file downloads.
# Tests commands of the form: {prog} FILENAME [--append|--replace|--print]


class TestFileDownloadNormal(BaseIntegrationTest):

    def test_clean_download(self):
        self._execute_client(TEST_FILE)
        self.assertEqual(self._read_output(TEST_FILE), TEST_STR)

    def test_default_backup(self):
        self._execute_client(RAND_FILE)
        self._execute_client(RAND_FILE)
        self.assertEqual(self._read_output(RAND_FILE),
                         self._read_output(RAND_FILE + self.BACKUP_SUFFIX))


class TestFileDownloadAppend(BaseIntegrationTest):
    """
    Test the --append option
    """

    def test_append(self):
        self._execute_client(TEST_FILE)
        self._execute_client(TEST_FILE, "--append")
        self.assertTrue(self._read_output(TEST_FILE))
        self.assertFalse(os.path.exists(self._path_in_tmpdir(TEST_FILE + self.BACKUP_SUFFIX)))

    def test_append_on_empty(self):
        self._execute_client(TEST_FILE, "--append")
        self.assertEqual(TEST_STR, self._read_output(TEST_FILE),
                         "--append on nonexistent file should create a new file")


class TestFileDownloadReplace(BaseIntegrationTest):
    """
    Test the --replace option
    """

    def test_replace(self):
        self._execute_client(TEST_FILE)
        self._execute_client(TEST_FILE, "--replace")
        self.assertFalse(os.path.exists(self._path_in_tmpdir(TEST_FILE + "gr.bak")))
        self.assertEqual(self._read_output(TEST_FILE), TEST_STR,
                         "--replace should replace existing file content")

    def test_append_replace_exclusive(self):
        # Check subprocess return status rather than @unittest.expectedFailure
        print "=========== Expecting error messages below..."
        self.assertTrue(self._execute_client(RAND_FILE, "-a", "-r") != 0)
        self.assertTrue(self._execute_client(RAND_FILE, "-a", "--replace") != 0)
        self.assertTrue(self._execute_client(RAND_FILE, "--append", "-r") != 0)
        self.assertTrue(self._execute_client(RAND_FILE, "--append", "--replace") != 0)

    def test_print(self):
        output = self._execute_client_output(TEST_FILE, "--print").strip()
        self.assertEqual(TEST_STR, output)
        self.assertFalse(os.path.exists(self._path_in_tmpdir(TEST_FILE)))


if __name__ == 'main':
    unittest.main()

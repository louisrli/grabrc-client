import unittest
import os
import sys
import shutil
from subprocess import call
from abstract_test_base import BaseIntegrationTest

"""
Integration test for file downloads.
Tests commands of the form:
   {prog} FILENAME [--append|--replace|--print]
"""


class TestFileDownload(BaseIntegrationTest):

    def _get_dirname(self):
        return "tmp_download_test"

    # Default
    def test_clean_download(self):
        self._execute_client(self.TEST_FILE)
        self.assertEqual(self._read_output(self.TEST_FILE), self.TEST_STR)

    def test_default_backup(self):
        self._execute_client(".emacs")
        self._execute_client(".emacs")
        self.assertEqual(self._read_output(".emacs"),
                         self._read_output(".emacs" + self.BACKUP_SUFFIX))

    # Append
    def test_append(self):
        self._execute_client(self.TEST_FILE)
        self._execute_client(self.TEST_FILE, "--append")
        self.assertTrue(self._read_output(self.TEST_FILE))
        self.assertFalse(os.path.exists(self._path_in_tmpdir(self.TEST_FILE + self.BACKUP_SUFFIX)))

    def test_append_on_empty(self):
        self._execute_client(self.TEST_FILE, "--append")
        self.assertEqual(self.TEST_STR, self._read_output(self.TEST_FILE),
                         "--append on nonexistent file should create a new file")

    # Replace
    def test_replace(self):
        self._execute_client(self.TEST_FILE)
        self._execute_client(self.TEST_FILE, "--replace")
        self.assertFalse(os.path.exists(self._path_in_tmpdir(self.TEST_FILE + "gr.bak")))
        self.assertEqual(self._read_output(self.TEST_FILE), self.TEST_STR,
                         "--replace should replace existing file content")

    def test_append_replace_exclusive(self):
        # Check subprocess return status rather than @unittest.expectedFailure
        print "Expecting error messages below..."
        self.assertTrue(self._execute_client(".emacs", "-a", "-r") != 0)
        self.assertTrue(self._execute_client(".emacs", "-a", "--replace") != 0)
        self.assertTrue(self._execute_client(".emacs", "--append", "-r") != 0)
        self.assertTrue(self._execute_client(".emacs", "--append", "--replace") != 0)

    def test_print(self):
        output = self._execute_client_output(self.TEST_FILE, "--print").strip()
        self.assertEqual(self.TEST_STR, output)
        self.assertFalse(os.path.exists(self._path_in_tmpdir(self.TEST_FILE)))


if __name__ == 'main':
    unittest.main()

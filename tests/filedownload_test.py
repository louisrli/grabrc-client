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
        self._execute_client(".vimrc")
        self.assertEqual(self._read_output(".vimrc"), self.vim_str)

    def test_default_backup(self):
        self._execute_client(".emacs")
        self._execute_client(".emacs")
        self.assertEqual(self._read_output(".emacs"),
                         self._read_output(".emacs.gr.bak"))

    # Append
    def test_append(self):
        self._execute_client(".vimrc")
        self._execute_client(".vimrc", "--append")
        self.assertTrue(self._read_output(".vimrc"))
        self.assertFalse(os.path.exists(self._path_in_tmpdir(".vimrc.gr.bak")))

    def test_append_on_empty(self):
        self._execute_client(".vimrc", "--append")
        self.assertEqual(self.vim_str, self._read_output(".vimrc"),
                         "--append on nonexistent file should create a new file")

    # Replace
    def test_replace(self):
        self._execute_client(".vimrc")
        self._execute_client(".vimrc", "--replace")
        self.assertFalse(os.path.exists(self._path_in_tmpdir(".vimrc.gr.bak")))
        self.assertEqual(self._read_output(".vimrc"), self.vim_str,
                         "--replace should replace existing file content")

    def test_append_replace_exclusive(self):
        # Check subprocess return status rather than @unittest.expectedFailure
        print "Expecting error messages below..."
        self.assertTrue(self._execute_client(".emacs", "-a", "-r") != 0)
        self.assertTrue(self._execute_client(".emacs", "-a", "--replace") != 0)
        self.assertTrue(self._execute_client(".emacs", "--append", "-r") != 0)
        self.assertTrue(self._execute_client(".emacs", "--append", "--replace") != 0)

    def test_print(self):
        output = self._execute_client_output(".vimrc", "--print").strip()
        self.assertEqual(self.vim_str, output)
        self.assertFalse(os.path.exists(self._path_in_tmpdir(".vimrc")))


if __name__ == 'main':
    unittest.main()

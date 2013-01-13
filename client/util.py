"""
Utility functions for output, executing commands, and downloading files.
"""

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import commands
import sys
import urllib2
import os
import shutil
from const import Const


def print_msg(prefix, msg):
    print "[%s] %s" % (prefix.upper(), msg)


def info(msg):
    print_msg("info", msg)


def warn(msg):
    print_msg("warning", msg)


def error(msg):
    print_msg("error", msg)


def success(msg):
    print_msg("success", msg)


def exit_runtime_error(*args):
    error("Oops! Something went wrong:\n-- %s" % "\n-- ".join(args))
    sys.exit(1)


def exec_cmd_status(cmd):
    """ Returns True on success, False on failure """
    return commands.getstatusoutput(cmd)[0] == 0


def exec_cmd_output(cmd):
    (status, output) = commands.getstatusoutput(cmd)
    return status == 0, output


def http_get_contents(url):
    try:
        return urllib2.urlopen(url).read()
    except urllib2.HTTPError, e:
        msg_404 = "If you're looking for a directory, did you add 'dir:' before the directory name?"

        if ("404" in e.__str__()):
            exit_runtime_error("The file wasn't found! (404).", msg_404)
        exit_runtime_error(e.__str__(), "Requested URL: %s" % url)


def untar_gz(targz):
    """ Untar and extract a .tar.gz """
    targz.extractall()
    targz.close()


def sanitize_path(path):
    """ Clean up a pathname """
    return os.path.normpath(os.path.expanduser(path)).strip()


def backup_file(filepath):
    """Backs up a file if it already exists. If a .bak file already exists,
    then it appends .bak to it again and backs it up."""
    if not os.path.exists(filepath):
        return
    elif os.path.exists(filepath):
        backup_path = filepath + Const.BACKUP_SUFFIX
        backup_file(backup_path + Const.BACKUP_SUFFIX)
        shutil.move(filepath, backup_path)


def check_git():
    """ Checks if git exists. Exits with a runtime error if it's not on the path. """
    if not exec_cmd_output("git"):
        exit_runtime_error("Couldn't find git! Are you sure it's \
        installed and on the PATH?")

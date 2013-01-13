#!/usr/bin/env python
# Packaging / release script
# Dependencies:
# -- ALL: git, setup_tools
# -- install: easy_install
# -- uninstall: pip
# -- rpm: rpmbuild / Redhat system

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

import sys
import os
import subprocess
from optparse import OptionParser

parser = OptionParser(usage="%prog [pypi|install|rpm|clean]")
parser.add_option("--skip-tests", action="store_true", )
(opts, args) = parser.parse_args()
action = args[0]

def shell(cmd):
    return subprocess.check_output(cmd, shell=True)

def run_tests():
    if not opts.skip_tests:
        shell("nosetests")

def sed_version(new_ver, filepath):
    # Handle Mac's BSD sed
    if shell("uname").strip() == 'Darwin':
        print "On Mac OS X..."
        sed_i = "''"
    else:
        print "On Linux..."
        sed_i = ""
    sed_cmd = "sed -i %s 's/version=\".*\"/version=\"%s\"/' %s" % (sed_i, new_ver, filepath)
    shell(sed_cmd)


# Update revision number
revno = shell("git shortlog | grep -E '^[ ]+\w+' | wc -l").strip()
print "Updating revision number of file to %s" % revno
sed_version("r%s" % revno, "./client/client.py")
print shell("grep '%s' client/client.py" % revno)

if action == "pypi":
    run_tests()
    if not args[1]:
        print "Provide a release number for pypi"
        sys.exit(1)
    sed_version(args[1], "./setup.py")
    print shell("./setup.py sdist bdist_egg upload")
if action == "rpm":
    run_tests()
    print shell("./setup.py bdist_rpm")
if action == "uninstall":
    print "[y/n]"
    shell("sudo pip uninstall grabrc-client")
if action == "install":
    print "Building egg..."
    shell("./setup.py bdist_egg")
    print "Installing egg..."
    print shell("sudo easy_install dist/*.egg")
if action == "clean":
    print "Cleaning..."
    shell("rm -rf build dist *egg-info*")
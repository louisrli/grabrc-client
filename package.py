#!/usr/bin/env python
# Packaging / release script
# Dependencies:
# -- ALL: git, setup_tools
# -- install: easy_install
# -- uninstall: pip
# -- rpm: rpmbuild / Redhat system

import os
import subprocess
from optparse import OptionParser

parser = OptionParser(usage="%prog [pypi|install|rpm|clean]")

(opts, args) = parser.parse_args()
action = args[0]

def shell(cmd):
    return subprocess.check_output(cmd, shell=True)

def run_tests():
    shell("nosetests")

# Handle Mac's BSD sed
if shell("uname").strip() == 'Darwin':
    print "On Mac OS X..."
    sed_i = "''"
else:
    print "On Linux..."
    sed_i = ""

# Update revision number
revno = shell("git shortlog | grep -E '^[ ]+\w+' | wc -l").strip()
print "Updating revision number of file to %s" % revno
sed_cmd = "sed -i %s 's/version=\".*\"/version=\"r%s\"/' client/client.py" % (sed_i, revno)
shell(sed_cmd)
print shell("grep '%s' client/client.py" % revno)


if action == "pypi":
    run_tests()
    print shell("./setup.py sdist bdist_egg upload")
if action == "rpm":
    run_tests()
    print shell("./setup.py bdist_rpm")
if action == "uninstall":
    shell("sudo pip uninstall grabrc-client")
if action == "install":
    print "Building egg..."
    shell("./setup.py bdist_egg")
    print "Installing egg..."
    print shell("sudo easy_install dist/*.egg")
if action == "clean":
    print "Cleaning..."
    shell("rm -rf build dist *egg-info*")
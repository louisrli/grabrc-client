#!/usr/bin/env python
# Packaging / release script
# Dependencies:
# -- ALL: git, setup_tools
# -- install: easy_install
# -- uninstall: pip
# -- rpm: rpmbuild / Redhat system

import sys
import os
import subprocess
from optparse import OptionParser

parser = OptionParser(usage="%prog [pypi RELEASE_VER|install|uninstall|rpm|clean]")
parser.add_option("--skip-tests", action="store_true", )
(opts, args) = parser.parse_args()

if len(args) == 0:
    parser.print_usage()
    sys.exit(1)

action = args[0]


def shell(cmd):
    return subprocess.check_output(cmd, shell=True)


def run_tests():
    if not opts.skip_tests:
        shell("nosetests")


def sed_version(new_ver, filepath):
    """ Use sed to replace a 'version=' string with the new revno"""
    # Handle Mac's BSD sed
    if shell("uname").strip() == 'Darwin':
        print "On Mac OS X..."
        sed_i = "''"
    else:
        print "On Linux..."
        sed_i = ""
    sed_cmd = "sed -i %s 's/version=\".*\"/version=\"%s\"/' %s" % (sed_i, new_ver, filepath)
    shell(sed_cmd)


def update_help_revno():
    """ Updates the revno in client.py --version """
    revno = shell("git shortlog | grep -E '^[ ]+\w+' | wc -l").strip()
    print "Updating revision number of file to %s" % revno
    sed_version("r%s" % revno, "./client/client.py")
    print shell("grep '%s' client/client.py" % revno)

if action == "pypi":
    run_tests()
    if not args[1]:
        print "Provide a release number for pypi"
        sys.exit(1)
    update_help_revno()
    sed_version(args[1], "./setup.py")
    print shell("./setup.py sdist bdist_egg upload")
if action == "rpm":
    update_help_revno()
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

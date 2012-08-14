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

def shell(cmd):
    return subprocess.check_output(cmd, shell=True)

parser = OptionParser(usage="%prog [pypi|install|rpm]")
(opts, args) = parser.parse_args()
action = args[0]

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
    shell("./setup.py sdist bdist_egg upload")
elif action == "rpm":
    shell("./setup.py bdist_rpm")
elif action =="install":
    print "Building egg..."
    shell("./setup.py bdist_egg")
    print "Installing egg..."
    print shell("sudo easy_install dist/*.egg")


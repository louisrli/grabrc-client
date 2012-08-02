import subprocess
import sys
import urllib2
import os
import shutil

def exit_runtime_error(*args):
    print "Oops! Something went wrong:\n-- %s" % "\n-- ".join(args)
    sys.exit(1)


def print_info(prefix, msg):
    print "[%s] %s" % (prefix.upper(), msg)


def exec_cmd(str):
    return subprocess.Popen(str.split(" "),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE).communicate()


def http_get_contents(url):
    try:
        return urllib2.urlopen(url).read()
    except urllib2.HTTPError, e:
        exit_runtime_error(e.__str__(), "Requested URL: %s" % url)


def untar_gz(targz):
    targz.extractall()
    targz.close()


def backup_file(filepath, suffix=".bak"):
    """Backs up a file if it already exists. If a .bak file already exists,
    then it appends .bak to it again and backs it up."""
    if not os.path.exists(filepath):
        return
    elif os.path.exists(filepath):
        backup_path = filepath + suffix
        shutil.move(filepath, backup_path)
        backup_file(backup_path + suffix, suffix)

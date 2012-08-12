import StringIO
import urllib2
import zipfile
import tarfile
import shutil
import util
import glob
from const import Const
import os
import logging
import sys

def _get_grabrc_archive(username, tar_or_zip):
    """
    Gets the repository for a certain user
    Returns a file object (zip or tar).
    """
    try:
        contents = urllib2.urlopen("%s/%s/repo/%s" % (Const.SERVER_URL, username, tar_or_zip))
    except urllib2.HTTPError, e:
        util.exit_runtime_error(e.__str__(), "Attempted to get %s archive" % tar_or_zip)

    file_as_str = StringIO.StringIO()
    file_as_str.write(contents.read())
    file_as_str.seek(0)

    if tar_or_zip == "targz":
        return tarfile.open(fileobj=file_as_str, mode="r:gz")
    elif tar_or_zip == "zip":
        return zipfile.ZipFile(contents, "r")

def _create_grabrc_folder(username, destdir, dirname):
    """
    Creates the local copy of the grabrc git repository if
    it doesn't already exist. If it does, update it accordingly
    """
    # Check if the repo exists
    repo_dirpath = os.path.join(destdir, dirname)

    # Sanity check: if they have a file named with the directory (they shouldn't))
    if os.path.isfile(repo_dirpath):
        util.print_msg("warning", "Found a file where there should be a git directory. \
        Backing up...")
        util.backup_file(repo_dirpath)

    # Make a temporary staging directory
    tmp_path = repo_dirpath + "/grabrctmp.d"

    def download_and_untar():
        """Downloads a tar from the server, untars, the files one directory up"""
        repo_targz = _get_grabrc_archive(username, "targz")
        util.untar_gz(repo_targz)
        os.renames(glob.glob("./%s-%s*" % (username, Const.REPO_NAME))[0], tmp_path)

    if os.path.isdir(repo_dirpath):
        print "Found an existing directory named %s in %s..." % (dirname, destdir)
        print "Backing up the directory..."
        util.backup_file(repo_dirpath)

    if not os.path.exists(repo_dirpath):
        util.print_msg("info", "Downloaded repository to %s" % repo_dirpath)
        os.mkdir(repo_dirpath)
        os.chdir(repo_dirpath)

        download_and_untar()
        # Move everything from the tmpdirectory to one level up
        repofiles = [os.path.join(tmp_path, filename)
                     for filename in os.listdir(tmp_path)]
        map(lambda f: shutil.move(f, repo_dirpath), repofiles)
        os.rmdir(tmp_path)  # Directory should be empty!


def download_repo_nongit(options):
    """Downloads and extracts the git repository to the local filesystem"""
    util.print_msg("info", "Downloading the repository...")

    if options.replace:
        shutil.rmtree(os.path.join(options.destdir, options.outfile or Const.DEFAULT_DIRNAME))
    elif options.append:
        util.print_msg("info", "Repository download doesn't support the --append option. \
                                Falling back to default behavior of backing up the existing \
                                directory")

    # Delegate to _create_grabrc_folder for backing up existing
    _create_grabrc_folder(options.github,
                        options.destdir,
                        options.outfile or Const.DEFAULT_DIRNAME)


def download_subdirectory(subdir_name, options):
    """
    Downloads and extracts only a certain subdirectory
    Works by downloading the whole repo and taking just the folder
    that we need.
    """
    util.print_msg("info", "Preparing to download the subdirectory %s" % subdir_name)
    TMPDIR_NAME = "grabrc.subdir.tmpd"
    TMPDIR_PATH = os.path.join(options.destdir, TMPDIR_NAME)
    TARGET_PATH = os.path.join(options.destdir, options.outfile or subdir_name)
    logging.debug("Subdirectory tmpdir: %s" % TMPDIR_PATH)
    logging.debug("Subdirectory target: %s" % TARGET_PATH)

    target_exists = os.path.exists(TARGET_PATH)
    if target_exists:
        if options.append:
            util.print_msg("warning", "Append option doesn't apply to directories. \
                                       Falling to default behavior of backing up \
                                       the existing directory")
        # Note that this is 'if' and not 'elif'
        if options.replace:
            util.print_msg("info", "Replacing the existing directory %s" % subdir_name)
            shutil.rmtree(TARGET_PATH)
        else:
            util.print_msg("warning", "Found an existing directory %s" % subdir_name)
            util.print_msg("warning", "Backing up existing directory %s to %s%s" %
                   (subdir_name, subdir_name, Const.BACKUP_SUFFIX))
            util.backup_file(TARGET_PATH)

    # Try to download the repository then move it to the current directory
    # _create_grabrc_folder will check if the directory already exists
    try:
        # Download the repository and move the subdirectory
        _create_grabrc_folder(options.github,
                              options.destdir,
                              TMPDIR_NAME)

        if not os.path.exists(os.path.join(TMPDIR_PATH, subdir_name)):
            util.exit_runtime_error("Couldn't find the subdirectory %s in the repository"
                                % subdir_name)

        os.renames(os.path.join(TMPDIR_PATH, subdir_name),
                    TARGET_PATH)
    except Exception as e:
        print e
    finally:
        # Clean up after ourselves
        shutil.rmtree(TMPDIR_PATH)


def download_file(filename, options):
    """Downloads a file from the grab-rc server"""

    FILE_URL = "%s/%s/%s" % \
        (Const.SERVER_URL, options.github, filename)

    logging.debug("FILE_URL: %s" % FILE_URL)

    contents = util.http_get_contents(FILE_URL)

    # Print and exit if --print is set
    if options.stdout:
        print contents
        sys.exit(0)

    # Use options if they exist, otherwise fall to defaults
    outfile = options.outfile or filename
    destdir = options.destdir
    target_path = os.path.join(destdir, outfile)
    backup_path = None
    file_exists = os.path.isfile(target_path)

    # Handle --append, --replace, or default (write to backup file if exists in `pwd`)
    if not file_exists or options.append:
        handle = open(target_path, "a+")
        if options.append:  # Make appending prettier
            handle.write("\n\n")
    elif options.replace:
        handle = open(target_path, "w+")
    elif file_exists:
        # Write the new file to the backup path rather than moving the existing file
        backup_path = target_path + Const.BACKUP_SUFFIX
        print "[WARNING] %s already exists! \nWriting to: [ %s ]" % (target_path, backup_path)
        handle = open(backup_path, "w+")
    else:
        util.exit_runtime_error("Please file a bug.", "(Unhandled file download mode)")

    logging.debug("(Outfile, Destination, Target)\n -- (%s, %s, %s)"
                  % (outfile, destdir, target_path))

    handle.write(contents)
    util.print_msg("success", "Downloaded %s to %s." % (filename, backup_path or target_path))

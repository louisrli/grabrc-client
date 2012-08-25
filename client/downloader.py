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
    Creates the local copy of the grabrc git repository in directory destdir
    with name dirname. The path destdir/dirname should not already exist
    """
    # Check if the repo exists
    repo_dirpath = os.path.join(destdir, dirname)
    tmp_path = os.path.join(repo_dirpath, "grabrctmp.d")

    def download_and_untar():
        """Downloads a tar from the server, untars one directory up"""
        repo_targz = _get_grabrc_archive(username, "targz")
        util.untar_gz(repo_targz)
        os.renames(glob.glob("./%s-%s*" % (username, Const.REPO_NAME))[0], tmp_path)

    # Sanity check: if they have a file named with the directory (they shouldn't))
    if os.path.isfile(repo_dirpath):
        util.warn("Found a file where there should be a git directory. \
                   Backing up...")
        util.backup_file(repo_dirpath)
    elif os.path.isdir(repo_dirpath):
        util.info("Found an existing directory named %s in %s..." % (dirname, destdir))
        util.info("Backing up the directory...")
        util.backup_file(repo_dirpath)

    if not os.path.exists(repo_dirpath):
        # Make a temporary staging directory
        util.print_msg("info", "Preparing repository directory at %s" % repo_dirpath)
        os.makedirs(repo_dirpath)
        os.chdir(repo_dirpath)

        download_and_untar()

        # Move everything from the tmpdirectory to one level up
        repofiles = [os.path.join(tmp_path, filename)
                     for filename in os.listdir(tmp_path)]
        map(lambda f: shutil.move(f, repo_dirpath), repofiles)  # os.rmdir requires empty dir
        os.rmdir(tmp_path)
    else:
        util.exit_runtime_error("The repository's target directory exists at %s \
        but should have been backed up to a different location. Race condition?" % repo_dirpath)

    util.success("Finished repository download.")


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

    util.info("Creating temporary directory paths...")

    if options.append:
        util.warn("Append option doesn't apply to directories. \
        Falling to default behavior of backing up \
        the existing directory")

    target_exists = os.path.exists(TARGET_PATH)
    if target_exists:
        if options.replace:
            util.info("Replacing the existing directory %s" % TARGET_PATH)
            shutil.rmtree(TARGET_PATH)
        else:
            util.warn("Found an existing directory %s" % TARGET_PATH)
            util.warn("Backing up existing directory %s to %s%s" %
                      (TARGET_PATH, TARGET_PATH, Const.BACKUP_SUFFIX))
            util.backup_file(TARGET_PATH)

    # Try to download the repository then move it to the current directory
    # _create_grabrc_folder will check if the directory already exists
    try:
        # Download the repository and move the subdirectory
        _create_grabrc_folder(options.github,
                              options.destdir,
                              TMPDIR_NAME)
        #os.makedirs(TMPDIR_PATH)  # Create the tmpdir again
        # We still use subdir_name, the original name
        if not os.path.exists(os.path.join(TMPDIR_PATH, subdir_name)):
            util.exit_runtime_error("Couldn't find the subdirectory %s in the repository" % subdir_name)

        shutil.move(os.path.join(TMPDIR_PATH, subdir_name), TARGET_PATH)
    finally:
        # Clean up after ourselves
        util.info("Cleaning up temporary directories...")
        shutil.rmtree(TMPDIR_PATH)

    util.success("Downloaded subdirectory %s to %s" % (subdir_name, TARGET_PATH))


def download_file(filename, options):
    """Downloads a file from the grabrc server"""
    FILE_URL = "%s/%s/%s" % \
        (Const.SERVER_URL, options.github, filename)

    logging.debug("FILE_URL: %s" % FILE_URL)

    contents = util.http_get_contents(FILE_URL)

    if options.stdout:
        print contents
        sys.exit(0)

    # Use options if they exist, otherwise fall to defaults
    outfile = options.outfile or filename
    destdir = options.destdir or os.getcwd()
    target_path = os.path.join(destdir, outfile)
    backup_path = target_path + Const.BACKUP_SUFFIX
    target_file_exists = os.path.isfile(target_path)

    # Handle --append, --replace, or default behavior (default is to backup a conflict)
    if not target_file_exists or options.append:
        handle = open(target_path, "a+")
        if options.append:
            handle.write("\n\n")  # Make appending prettier
    elif options.replace:
        handle = open(target_path, "w+")
    elif target_file_exists:
        # Backup the existing file and then write the new file
        util.warn("A file already exists at %s! Moving it to a backup at: %s"
                  % (target_path, backup_path))
        util.backup_file(target_path)
        handle = open(target_path, "w+")
    else:
        util.exit_runtime_error("Please file a bug.",
                                "(File download doesn't seem to cover all option cases)")

    logging.debug("(Outfile, Destination, Target)\n -- (%s, %s, %s)"
                  % (outfile, destdir, target_path))

    handle.write(contents)
    util.success("Downloaded %s to %s." % (filename, target_path))

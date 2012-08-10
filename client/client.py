#!/usr/bin/python

from optparse import OptionParser, OptionGroup
import StringIO
import urllib2
import os
import sys
import logging
import glob
import zipfile
import tarfile
import shutil
import util
import uploader
from const import Const

logging.basicConfig(level=logging.INFO)


def main():
    """
    Parses command line options, then delegates to various other functions.
    """

    # TODO add description of default options
    parser = OptionParser(usage="%prog [options] ['repo'| FILENAME | dir:DIRECTORY] [save ...]",
                          version="0.1 alpha")

    topgroup = OptionGroup(parser, "General")
    topgroup.add_option("-o", "-O", "--name", "--outfile",
                        dest="outfile", action="store", metavar="FILE",
                        help="Rename the output file/directory.")

    topgroup.add_option("-d", "--destdir",
                        dest="destdir", action="store", metavar="DIR",
                        help="Place downloaded file/directory in the given directory. \
                        Default: The current working directory.")

    topgroup.add_option("--no-backup",
                        dest="nobackup", action="store_true",
                        help="If the file already exists, don't make a backup.")

    directorygroup = OptionGroup(parser, "Directories")
    directorygroup.add_option("-k", "--keep-tar",
                              dest="tar", action="store_true",
                              help="Download the directory as a tar. \
                              Default: Untar the directory")

    directorygroup.add_option("-z", "--keep-zip",
                              dest="zip", action="store_true",
                              help="Download the directory as a .zip.")

    filegroup = OptionGroup(parser, "Files")
    filegroup.add_option("-a", "--append",
                         dest="append", action="store_true",
                         help="If file already exists, append to existing file")

    filegroup.add_option("-r", "--replace",
                         dest="replace", action="store_true",
                         help="If the file already exists, replace it")

    filegroup.add_option("-p", "--print",
                         dest="stdout", action="store_true",
                         help="Print the file to stdout")

    savegroup = OptionGroup(parser, "Saving")
    savegroup.add_option("-m", "--message",
                         dest="message",
                         help="A commit message for saving a file to Github")

    # Validate and parse options, set mode
    map(parser.add_option_group,
        [topgroup, filegroup, directorygroup])

    (opts, args) = parser.parse_args()
    logging.debug("Options and arguments: %s / %s" % (opts, args))

    # Simple substitute for logging
    def usage_exit(level, reason):
        parser.print_usage()
        print "[%s] %s" % (level.upper(), reason)
        sys.exit(1)

    try_msg = "Try either 'FILE' to download a file or 'save FILE' " \
              "to save a file"

    # Validate options: number of arguments
    if len(args) > 2:
        usage_exit("error", "Invalid number of arguments ( > 2). " + try_msg)

    # Validate options: either "save" or empty
    mode = "download"
    if len(args) == 1:
        arg = args[0]
        if arg == "save":
            usage_exit("error", "Please specify a file to save.")
        elif arg == "repo":
            mode = "repo"
        else:
            download_name = arg
    elif "save" in args:
        mode = "upload"
        upload_filepath = (n for n in args if n != "save").next()
    else:
        usage_exit("error", "Invalid arguments. " + try_msg)

    # Validate options: Invalid combinations
    if opts.append and opts.replace:
        usage_exit("error", "Both --append and --replace were selected. Please select one.")
    if opts.zip and opts.tar:
        usage_exit("error", "Both --keep-zip and --keep-tar were selected. Please select one.")

    # Set defaults
    opts.destdir = opts.destdir or os.getcwd()
    opts.destdir = util.sanitize_path(opts.destdir)
    if opts.outfile:
        opts.outfile = util.sanitize_path(opts.outfile)

    # Check config file (~/.grabrc) for Github username
    configpath = "%s/.grabrc" % os.path.expanduser("~")

    if opts.__dict__.get('github'):
        github_acc = opts.github

    # Interactively prompt for username if ~/.grabrc does not exist
    if not os.path.isfile(configpath):
        print """\
        ========================================================
        Welcome! This seems to be your first time starting %s.
        Please enter your Github username.
        %s will search for files in the repository named %s""" \
        % (Const.PROG_NAME, Const.PROG_NAME, Const.REPO_NAME)

        github_acc = raw_input('-- Github account: ')
        cfile = open(configpath, 'w+')
        cfile.write(github_acc)
    else:
        cfile = open(configpath, 'r+')
        github_acc = cfile.readline().strip()
    cfile.close()

    opts.github = github_acc

    # If CLI options don't override account, use this one
    logging.debug("Github account: %s" % github_acc)

    # Execute actual script
    DIR_PREFIX = "dir:"
    if mode == "upload":
        uploader.save(upload_filepath, opts)
    elif mode == "download":
        if download_name.startswith(DIR_PREFIX):
            _download_subdirectory(download_name[len(DIR_PREFIX):], opts)
        else:
            _download_file(download_name, opts)
    elif mode == "repo":
        _download_repo_nongit(opts)

################################################################################
# Utility functions for downloading, printing, exiting
################################################################################

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

################################################################################
# Main functions
################################################################################

def _download_repo_nongit(options):
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


def _download_subdirectory(subdir_name, options):
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
        print os.listdir(options.destdir)  # TODO remove debug
        print "destdir:%s" % options.destdir  # TODO remove debug
    except Exception as e:
        print e
    finally:
        # Clean up after ourselves
        shutil.rmtree(TMPDIR_PATH)


def _download_file(filename, options):
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


def _upload_file(filename, options):
    #_create_grabrc_folder(options.github)
    # Checkout grabrc repo
    # Copy the target file to the top level directory
    # Commit it with some timestamped, automatic messgae
    pass


if __name__ == '__main__':
    main()

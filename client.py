#!/usr/bin/python

from optparse import OptionParser, OptionGroup
import urllib2
import os
import sys
import logging

logging.basicConfig(level=logging.DEBUG)

REPO_NAME = "grabrc-repo"
PROG_NAME = "grabrc"
SERVER_URL = "http://grabrc.heroku.com"


def main():
    """
    Parses command line options, then delegates to various other functions.
    """

    # TODO add description of default options
    parser = OptionParser(usage="%prog [options] ['repo'| FILENAME | dir:DIRECTORY] [save ...]",
                          version="0.1 alpha")
    topgroup = OptionGroup(parser, "General")
    filegroup = OptionGroup(parser, "Files")
    directorygroup = OptionGroup(parser, "Directories")

    topgroup.add_option("-o", "-O", "--name",
                        dest="outfile", action="store", metavar="FILE",
                        help="Rename the output file/directory.")

    topgroup.add_option("-d", "--destdir",
                        dest="destdir", action="store", metavar="DIR",
                        help="Place downloaded file/directory in the given directory. \
                        Default: The current working directory.")

    topgroup.add_option("--no-backup",
                        dest="nobackup", action="store_true",
                        help="If the file already exists, don't make a backup.")

    directorygroup.add_option("-k", "--keep-tar",
                              dest="tar", action="store_true",
                              help="Download the directory as a tar. \
                              Default: Untar the directory")

    directorygroup.add_option("-z", "--keep-zip",
                              dest="zip", action="store_true",
                              help="Download the directory as a .zip.")

    filegroup.add_option("-a", "--append",
                         dest="append", action="store_true",
                         help="If file already exists, append to existing file")

    filegroup.add_option("-r", "--replace",
                         dest="replace", action="store_true",
                         help="If the file already exists, replace it")

    filegroup.add_option("-p", "--print",
                         dest="stdout", action="store_true",
                         help="Print the file to stdout")

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

    try_msg = "Try either 'save FILE' or 'FILE'"

    # Validate options: number of arguments
    len(args) > 2 and usage_exit("error", "Invalid number of arguments ( > 2). " + try_msg)

    # Validate options: either "save" or empty
    mode = "download"
    if len(args) == 1:
        download_name = args[0]
    elif "save" in args:
        mode = "upload"
        upload_filepath = (n for n in args if n != "save")
    else:
        usage_exit("error", "Invalid arguments. " + try_msg)

    # Validate options: Invalid combinations
    if opts.append and opts.replace:
        usage_exit("error", "Both --append and --replace were selected. Please select one.")
    if opts.zip and opts.tar:
        usage_exit("error", "Both --keep-zip and --keep-tar were selected. Please select one.")

    # Check config file (~/.grabrc) for Github username
    configpath = "%s/.grabrc" % os.path.expanduser("~")

    if opts.__dict__.get('github'):
        github_acc = opts.github
    if (not os.path.isfile(configpath)):
        print """\
        ========================================================
        Welcome! This seems to be your first time starting %s.
        Please enter your Github username.
        %s will search for files in the repository named %s""" \
        % (PROG_NAME, PROG_NAME, REPO_NAME)

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
        if upload_name.startswith(DIR_PREFIX):
            pass
        else:
            _upload_file(upload_filepath, opts)
    elif mode == "download":
        if download_name.startswith(DIR_PREFIX):
            # TODO
            _download_directory(download_name, opts)
        else:
            _download_file(download_name, opts)


def _exit_runtime_error(*args):
    print "Oops! Something went wrong:\n-- %s" % "\n-- ".join(args)
    sys.exit(1)


def _print_info(prefix, msg):
    print "[%s] %s" % (prefix.upper(), msg)


def _http_get_contents(url):
    try:
        return urllib2.urlopen(url).read()
    except urllib2.HTTPError, e:
        _exit_runtime_error(e.__str__(), "Requested URL: %s" % url)


def _download_directory(dirname, options):
    pass


def _create_git_repo():
    """
    Creates the local copy of the grabrc git repository if
    it doesn't already exist. If it does, update it accordingly
    """

    # Check for git
    if not subprocess.call("git"):
        _exit_runtime_error("Couldn't find git! Are you sure it is \
        installed and on the PATH.")

    # Check if it exists
    if not os.path.exists(git_dirpath):
        os.mkdir(git_dirpath)
    git_dirpath = os.path.expanduser("~/.grabrc.git")

    # Check if it's a git repo
    if not os.path.exists(git_dirpath + "/.git/"):
        os.chdir(git_dirpath)
        subprocess.call(["git", "init"])
        # TODO




def _upload_file(filename, options):
    pass
    # Checkout grabrc repo
    # Copy the target file to the top level directory
    # Commit it with some timestamped, automatic messgae
    pass


def _download_file(filename, options):
    """Downloads a file from the grab-rc server"""

    FILE_URL = "%s/%s/%s" % \
        (SERVER_URL, options.github, filename)

    logging.debug("FILE_URL: %s" % FILE_URL)

    contents = _http_get_contents(FILE_URL)

    # Print and exit if --print is set
    if options.stdout:
        print contents
        sys.exit(0)

    # Use options if they exist, otherwise fall to defaults
    outfile = options.outfile or filename
    destdir = options.destdir or os.getcwd()
    target_path = destdir + "/" + outfile
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
        backup_path = target_path + ".gr.bak"
        print "[WARNING] %s already exists! \nWriting to: [ %s ]" % (target_path, backup_path)
        handle = open(backup_path, "w+")
    else:
        _exit_runtime_error("Please file a bug.", "(Unhandled file download mode)")

    logging.debug("(Outfile, Destination, Target)\n -- (%s, %s, %s)"
                  % (outfile, destdir, target_path))

    handle.write(contents)
    _print_info("success", "Downloaded %s to %s." % (filename, backup_path or target_path))

if __name__ == '__main__':
    main()

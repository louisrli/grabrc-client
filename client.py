#!/usr/bin/python

from optparse import OptionParser, OptionGroup
import urllib2
import fileinput
import os
import sys
import logging

logging.basicConfig(level=logging.DEBUG)

PROG_NAME="grabrc"
REPO_NAME="grabrc-repo"

def main():
    parser = OptionParser(usage="%prog [options] ['repo'| FILENAME | dir:DIRECTORY] [save ...]",
                          version="0.1 alpha")
    topgroup = OptionGroup(parser, "General")
    filegroup = OptionGroup(parser, "Files")
    directorygroup = OptionGroup(parser, "Directories")

    topgroup.add_option("-o", "-O",  "--name",
                        dest="outfile", action="store", metavar="FILE",
                        help="Rename the output file to the given name.")

    topgroup.add_option("-d", "--destdir",
                        dest="destdir", action="store", metavar="DIR",
                        help="Place the downloaded file in the given directory")

    directorygroup.add_option("-k", "--keep-tar",
                              dest="tar", action="store_true",
                              help="Don't untar a directory or repo when downloaded.")

    filegroup.add_option("-a", "--append",
                         dest="append", action="store_true",
                         help="If the file already exists, append to the existing file")

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
        upload_name = (n for n in args if n != "save")
    else:
        usage_exit("error", "Invalid arguments. " + try_msg)

    # Validate options: Invalid combinations
    if opts.append and opts.replace:
        usage_exit("error", "Both --append and --replace were selected. Please select one.")

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
        github_acc = cfile.readline()
    cfile.close()

    opts.github = github_acc



    # If CLI options don't override account, use this one
    logging.debug("Github account: %s" % github_acc)

    # Execute actual script
    DIR_PREFIX="dir:"
    if mode == "upload":
        if upload_name.startswith(DIR_PREFIX):
            pass
        else:
            pass
    elif mode == "download":
        if download_name.startswith(DIR_PREFIX):
            download_directory(download_name, opts) #todo
        else:
            download_file(download_name, opts) #todo


        # Tests
        # Test if prompts when file exists (pos, neg)
        # Test options being correct
        # Test basic cli arguments (e.g. not save, etc.)

def exit_runtime_error(*args):
    print "Oops! Something went wrong:\n-- %s" % "\n-- ".join(args)
    sys.exit(1)

def print_info(prefix, msg):
    print "[%s] %s" % (prefix.upper(), msg)

def http_get_contents(url):
    try:
        return urllib2.urlopen(url).read()
    except urllib2.HTTPError, e:
        exit_runtime_error(e.__str__(), "Requested URL: %s" % url)

def download_directory(dirname, options):
    pass

def download_file(filename, options):
    FILE_URL = "https://raw.github.com/%s/%s/master/%s" % \
      (options.github, REPO_NAME, filename)
    logging.debug("FILE_URL: %s" % FILE_URL)

    contents = http_get_contents(FILE_URL)

    # Print and exit if --print is set
    if options.stdout:
        print contents
        sys.exit(0)

    # Use options if they exist, otherwise fall to defaults
    outfile = options.outfile or filename
    destdir = options.destdir or os.getcwd()
    target_path = destdir + "/" + outfile
    file_exists = os.path.isfile(target_path)

    if not file_exists or options.append:
        handle = open(target_path, "a+")
        if options.append: handle.write("\n\n") # Make appending prettier
    elif options.replace:
        handle = open(target_path, "w+")
    elif file_exists:
        backup_path = target_path + ".gr.bak"
        print "[WARNING] %s already exists! \nWriting to: [ %s ]" % (target_path, backup_path)
        handle = open (backup_path, "w+")
    else:
        exit_runtime_error("Please file a bug.", "(Unhandled file download mode)")

    logging.debug("(Outfile, Destination, Target)\n -- (%s, %s, %s)" \
                    % (outfile, destdir, target_path))

    handle.write(contents)
    print_info("success", "Downloaded %s to %s." % (filename, target_path))

if __name__ == '__main__':
    main()

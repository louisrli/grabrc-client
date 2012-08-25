import os
import sys
import logging
import shutil
import util
from const import Const


def save(source_path, options):
    """
    Save a directory or file by overwriting and pushing to git.
    Only allows saving to a top-level directory or file.
    """
    util.check_git()

    ssh_url = "git@github.com:%s/%s.git" % (options.github, Const.REPO_NAME)
    repo_url = "https://github.com/%s/%s.git" % (options.github, Const.REPO_NAME)

    tmp_repo = os.path.expanduser("~/%s" % Const.TMP_GIT_DIR)
    basename = options.outfile or os.path.basename(util.sanitize_path(source_path))
    path_in_repo = os.path.join(tmp_repo, basename)

    if not os.path.exists(source_path):
        util.exit_runtime_error("There doesn't seem to be a file or directory at %s" % source_path)

    if os.path.isdir(tmp_repo):
        # TODO - Add a local repository to be optimized, git reset hard head
        # Currently, it deletes the repository each time
        shutil.rmtree(tmp_repo)  # Remove the old repo to be completely to be safe

    # Clone the repo
    util.info("Cloning the git repository...")
    util.info("Trying to clone via SSH first.")
    if not util.exec_cmd_status("git clone %s %s" % (ssh_url, tmp_repo)):
        util.info("Couldn't clone via SSH, trying https://...")
        util.info("Since we're not using SSH," +
                  "Github will prompt for your username and password.")
        util.info("We don't store it!")
        (status, output) = util.exec_cmd_output("git clone %s %s" % (repo_url, tmp_repo))
        if not status:
            util.exit_runtime_error("Failed to clone git repository: %s" % output)

    # Move target file / directory over
    try:
        if os.path.isfile(source_path):
            shutil.copy2(source_path,
                         path_in_repo)
        elif os.path.isdir(source_path):
            # shutil.copytree doesn't overwrite an existing directory
            shutil.rmtree(path_in_repo)
            shutil.copytree(source_path,
                            os.path.join(tmp_repo, basename))
    except IOError, e:
        util.exit_runtime_error(
            "Error while trying to move contents to the git repository: %s" % e)

    os.chdir(tmp_repo)
    util.info("Adding files to git repository...")
    if not util.exec_cmd_status("git add %s" % basename):
        util.exit_runtime_error("Failed to add files to git repository")

    util.info("Committing to git repository...")
    (status, output) = util.exec_cmd_output(
        "git commit -m \"%s\"" %
        ("[grabrc-client] %s" % (options.message or source_path)))
    if not status:
        util.exit_runtime_error("Failed to commit files: %s" % output)

    util.info("Pushing to Github...")
    (status, output) = util.exec_cmd_output("git push")
    util.info("[git push] %s" % output)
    if not status:
        util.exit_runtime_error("Failed to push to the git repository.")
    else:
        util.info("Push successful.")

    util.success("Saved %s to Github." % source_path)

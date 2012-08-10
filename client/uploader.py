import os
import sys
import logging
import shutil
import util
from const import Const

def save(pathname, options):
    """
    Save a directory or file by overwriting and pushing to git.
    Only allows saving to a top-level directory or file.
    """
    util.check_git()

    ssh_url = "git@github.com:%s/%s.git" % (options.github, Const.REPO_NAME)
    repo_url = "https://github.com/%s/%s.git" % (options.github, Const.REPO_NAME)

    tmp_repo = os.path.expanduser("~/%s" % Const.TMP_GIT_DIR)
    basename = os.path.basename(util.sanitize_path(pathname))

    if os.path.isdir(tmp_repo):
        shutil.rmtree(tmp_repo)  # Remove it completely to be safe

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
        if os.path.isfile(pathname):
            shutil.copy2(pathname, tmp_repo)
        elif os.path.isdir(pathname):
            shutil.copytree(pathname,
                os.path.join(tmp_repo, options.outfile or basename))
    except IOError as e:
        util.exit_runtime_error(
            "Error while trying to move contents to the git repository: %s" % e)

    os.chdir(tmp_repo)
    util.info("Adding files to git repository...")
    if not util.exec_cmd_status("git add %s" % basename):
        util.exit_runtime_error("Failed to add files to git repository")

    util.info("Committing to git repository...")
    (status, output) = util.exec_cmd_output(
        "git commit -m \"%s\"" %
        ("[grabrc-client] %s" % (options.message or pathname)))
    if not status:
        util.exit_runtime_error("Failed to commit files: %s" % output)

    util.info("Pushing to Github...")
    (status, output) = util.exec_cmd_output("git push")
    util.info("[git push] %s" % output)
    if not status:
        util.exit_runtime_error("Failed to push to the git repository.")
    else:
        util.info("Push successful.")

    util.info("Saved file successfully.")






"""
Holds constant values relating to grabrc
"""

class Const:
    REPO_NAME = "grabrc-repo"  # Expected repo on Github
    PROG_NAME = "grabrc"
    SERVER_URL = "http://grabrc.heroku.com"
    BACKUP_SUFFIX = ".grbak"  # Default suffix for backup
    DEFAULT_DIRNAME = "grabrc.d"  # Default directory name when downloading a repo
    TMP_GIT_DIR = ".grabrc-git"  # Temporary directory used when saving items
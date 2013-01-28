"""
Holds constant values relating to grabrc
"""

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

class Const:
    TAR_NAME = "master"
    REPO_NAME = "grabrc-repo"  # Expected repo on Github
    PROG_NAME = "grabrc"
    SERVER_URL = "http://grabrc.heroku.com"
    BACKUP_SUFFIX = ".grbak"  # Default suffix for backup
    DEFAULT_DIRNAME = "grabrc.d"  # Default directory name when downloading a repo
    TMP_GIT_DIR = ".grabrc-git"  # Temporary directory used when saving items
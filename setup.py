#!/usr/bin/env python

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

from setuptools import setup

setup(name='grabrc-client',
      version="0.4",
      description='Lightweight, portable Github wrapper. \
Retrieval of dotfiles (.emacs, .vimrc, etc.) in any environment',
      author='Louis Li',
      url='http://www.github.com/louisrli/grabrc-client/',
      author_email='pong@outlook.com',
      packages=['client'],
      entry_points = {
          'console_scripts': ['grabrc = client.client:main']
      }

    )

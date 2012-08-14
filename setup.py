#!/usr/bin/env python

from setuptools import setup

setup(name='grabrc-client',
      version="0.2",
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

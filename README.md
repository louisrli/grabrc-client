# Overview

**grabrc-client** (referred to as **grabrc**) is a command-line tool for accessing and saving dotfiles from any terminal with Python 2.5+. This is particularly useful for frequent work with virtual machines, Amazon EC2, or new computers, where a new command line environment needs to quickly be brought up-to-date.

grabrc is a thin wrapper around Github, storing dotfiles in a Github repository. After you register your Github user name, create a repository, and store your files, downloading a file is as easy as:

```
$ grabrc .emacs
[SUCCESS] Downloaded .emacs to /Users/louis/.emacs.
```

# Installation

grabrc is on [PyPi](http://pypi.python.org/pypi/grabrc-client/) and can be installed via `easy_install` or [pip](http://www.pip-installer.org/en/latest/).

## via pip
```
$ pip install grabrc-client
```

## via easy_install
```
$ easy_install grabrc-client
```

# Setup

Create a repository named **grabrc-repo** on Github. You're then good to go!
 
# Usage

The first time that you run grabrc, you will be prompted for your Github username. This can be changed at any time in the file `~/.grabrc`.

## Storing or updating files to Github
Use `grabrc push /path/to/file` in order to store a file or folder to Github.

### Examples
```
$ grabrc push .vimrc
```

## Downloading a file
To download a file or directory from the repository, run `grabrc filename`. If it is a directory, prepend the file name with `dir:` (`grabrc dir:.emacs.d`). grabrc will automatically backup an existing file if a file or directory with the same name in the target directory.

### Examples
```
$ grabrc .emacs
$ grabrc dir:.emacs.d
$ grabrc .emacs --destdir /tmp
```

## Downloading the repository
You can quickly download the whole repository by running `grabrc repo`

## Options
`grabrc --help` will give a full list of options.

```
$ grabrc --help
Usage: 
grabrc OPTION [FILENAME | dir: DIRECTORY | repo] | Download a file from Github
grabrc push OPTION [FILEPATH | DIRPATH]          | Push a file to Github

Examples:
`grabrc .emacs`  -- Download .emacs from Github.
`grabrc dir:.emacs.d --outfile .irssiconfig` - Download the .emacs.d directory from Github.
`grabrc repo --destdir=/tmp/` -- Download and untar the repository in /tmp/.
`grabrc push /home/user/.vimrc` -- Save ~/.vimrc to Github, overwriting the existing .vimrc.


Options:
--version             show program's version number and exit
-h, --help            show this help message and exit

Download: All (files, directories, repositories):
-o NAME, -O NAME, --name=NAME, --outfile=NAME
Rename the downloaded item to NAME.
-d DIR, --destdir=DIR
Place the downloaded item in DIR.
Default: The current directory.
--no-backup         If the file already exists, don't make a backup.
Default: False. If the item already exists, it will be
backed up.

Download: Files:
-a, --append        If file already exists, append to existing file.
Default: Back up existing file
-r, --replace       If the file already exists, replace it
-p, --print         Print the file to the console instead of saving it.

Download: Repositories:
-k, --keep-tar      Download the repository as a tar.gz file.
Default: Untar the repository.
-z, --keep-zip      Download the repository as a .zip.
```

# Server

grabrc runs a server, a thin wrapper around Github. Its source code can be found [here](https://github.com/louisrli/grabrc-server).
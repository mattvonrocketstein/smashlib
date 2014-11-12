[quickstart](#quickstart) | [installation](#installation) | [testing](#testing) |

-------------------------------------------------------------------------------

features: [overview](#overview) | [project manager](#pm)

**Under Construction: porting to IPython==3.0.0-dev**

<a name="about"/>
ABOUT
=====
SmaSh is the smart-shell.  It offers features for project management, a flexible plugin architecture that is easy to use, and simple JSON configuration files that try to be as sane as possible.  Python developers will be particularly interested because it also happens to be a python/bash hybrid which builds on the pysh profile for IPython.  It leverages all existing system tab completion setup, apart from IPython's completion in python namespaces.  It builds on, and offers very sophisticated support for python virtual environments.


<a name="quickstart"/>
QUICKSTART
==========

```shell
  $ git clone https://github.com/mattvonrocketstein/smashlib.git ~/.smash
  $ cd ~/.smash
  $ virtualenv --no-site-packages .
  $ ./bin/pip install -r install_requirements.txt
  $ ./bin/python install.py
  $ ~/bin/smash
```

<a name="installation"/>
INSTALLATION
============

There are two parts to SmaSh: smashlib and the smash shell.  The instructions in the [quickstart section](#quickstart) install *both*.  Installing the shell is atypical because smash requires a development version of ipython, and smashlib will be installed to own it's own sandboxed python virtual environment.  **If you only want to develop against smashlib**, installation is more typical:

```shell
  $ git clone https://github.com/mattvonrocketstein/smashlib.git
  $ cd smashlib
  $ python setup.py develop
  $ pip install -r requirements.txt
```


<a name="overview"/>
Overview
=========

####Shell & Python Support
SmaSh functions seamlessly as a normal system shell, but it also a full fledged python interpretter.  It does shell stuff in the shell places, and python stuff in the python places.  If you're a bash user or an ipython user, your existing configuration efforts can be [inherited automatically](#TODO-config-inheritance).

####Tab-completion system
Depending on the context, tab completion information is derived either from ipython (for python namespaces, ipython aliases, etc) or directly from the system shell (for system commands, VCS subcommands, debian packages, whatever).  A few observations about this setup:

1. smash's completion system is at least as robust as your default shell
2. complete support for IPython's invaluable completion/readline facilities
3. if you want to write a new completer you have options: ipython way or the bash way

####Python Virtualenv Support
SmaSh has sophisticated virtualenv support which useful particularly if you're working on multiple projects or working with multiple major versions of the same software.  Activating/deactivating venvs is done with `venv_activate some_dir` and `venv_deactivate`, respectively.  This not only updates your $PATH, but updates the python runtime.  Modules from the new environment can now be imported directly, and side-effects from the old virtualenv are purged.

####Prompts
By default smash ships with the wonderfully dynamic [liquidprompt tool](#https://github.com/nojhan/liquidprompt).  Liquidprompt has it's own rich options for configuration and it's recommended that you [configure it in the normal way](https://github.com/nojhan/liquidprompt#features-configuration), but, some of these options can be overridden from `~/.smash/config.py`.  The default liquidprompt configuration features a prompt that shows activated virtual environments, as well as VCS branch and commit-or-stash-status.  Other options include everything from cpu/battery status to write-permissions for the current directory.

<a name="pm"/>
Project Manager
===============
Projects are natural abstractions for lots of kinds of work, and will be particularly familiar to anyone who has used an IDE.  In SmaSh, projects are defined by a nickname and associated with a directory.  Project can function as bookmarks that can be jumped to, and a project can have it's own set of command aliases and macros which other projects do not share.  Projects also have *types*, which can either be specified or autodetected based on the contents of the project directory.

**Project Types** are simply lists of strings, such as ["python"], or ["python", "docs"].  The type of a project may be provided by the user or autodetected by smash.  New user-defined types are encouraged, but they won't have default operations (see below).

**Project Operations** are things you can do to your projects, specifically *add*, *activate*, *build*, *check*, *test*, and *deactivate*.  Each operation can be user-specified per project as a list, where the list contains a sequence of shell commands or python callables.  If a given operation is not defined for a given project, a reasonable default for that operation should be guessed based on that project's type.  For each operation, here are some examples of the type of actions you might like to perform:

* Add: register new project nickname & directory with the Project Manager
* Activate: pull fresh code, start project-specific database services or system daemons.
* Build: maybe tox for a python project, ant for java or whatever
* Check: verify symlinks, start linters or other static analysis
* Test: set environment variables and then run unittests
* Deactivate: push finished code, stop project-specific database services or system daemons.

In the sections below, you will find instructions on how to invoke operations and what the default operations will involve for each project type.

-------------------------------------------------------------------------------

**Adding Projects** can be accomplished temporarily with `add_project nickname dir`, or new projects can be permanently added in `~/.smash/config.py`.  If you have a single directory like *~/code* that contains multiple projects, you can turn each subdirectory into a project by settings `project_search_dir` in the config file.

-------------------------------------------------------------------------------

**Activating Projects** is done with a command like `proj.nickname`.  (Note: you can use tab-completion over project names).
* Vagrant projects:
    * run "vagrant up"
* Python projects:
    * jump to the project's base directory
    * if the project contains one or more virtualenv's, the most recent will be activated

-------------------------------------------------------------------------------

**Deactivating Projects** usually isn't necessary because activating a new project will automatically deactivate the previous project.  To manually deactivate the current project, type `proj._deactivate`[#](#TODO),
* Vagrant projects:
    * run "vagrant halt"
* Python projects:
    * deactivate any virtual environment's associated with project ([see also](#))

-------------------------------------------------------------------------------

**Building Projects** is done only after a project is already activated.  If you have activated your project, then building it is done with `proj._build`.
* Python projects:
    * if tox.ini is present
        * runs `tox $TOX_ARGS` *(set TOX_ARGS in the activation rules)*
    * if setup.py is present run "setup.py develop"
* Doc projects:
    * if there is a README markdown file, generate github style html

-------------------------------------------------------------------------------

**Checking Projects** is done only after a project is already activated.  If you have activated your project, then checking it is done with `project._check`.
* Python projects:
    * run flake8 but ignore any venvs

-------------------------------------------------------------------------------

<a name="testing"/>
TESTING
=======

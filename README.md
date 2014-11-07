[about](#about) | [quickstart](#quickstart) | [installation](#installation) | [usage](#usage) | [testing](#testing) |

**Under Construction: porting to IPython==3.0.0-dev**

<a name="about"/>
ABOUT
=====
SmaSh is the smart-shell.  It offers features for project management, a flexible plugin architecture that is easy to use, and simple JSON configuration files that try to be as sane as possible.  Python developers might be particularly interested because it also happens to be a python/bash hybrid which builds on the pysh profile for IPython.  It builds on, and offers very sophisticated support for python virtual environments.


<a name="quickstart"/>
QUICKSTART
==========

```shell
  $ mkdir ~/.smash && cd ~/.smash
  $ git clone https://github.com/mattvonrocketstein/smashlib.git .
  $ python install.py
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

<a name="usage"/>
USAGE
=====

<a name="testing"/>
TESTING
=======

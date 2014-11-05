# -*- coding: utf-8
# User-configuration file for SmaSh.
#
# For examples of stuff you might like to do in here, check out:
#
#  1) default ipython config: ~/.ipython/profile_default/ipython_config.py
#  2) default smash config: ~/.smash/profile_SmaSh/ipython_config.py
#
# Note that while the main configuration file at ~/.smash/profile_SmaSh
# cannot be edited, you can make any overrides you would like to make there
# in here instead.
#
print '..loading SmaSh user-config from:', __file__

c = get_config()

# add custom directory hooks here
c.ChangeDirHooks.change_dir_hooks.append(
    "smashlib.ipy_cd_hooks.ChangeDirHooks.test_change_message")

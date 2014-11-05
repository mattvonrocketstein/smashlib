#!/usr/bin/env python
#
# you would think that "env python" would work everywhere, but due
# due to interaction with sourced venv's this is actually a tricky
# business..
import os, sys
import shutil

expanduser = os.path.expanduser
main_profile_name = 'SmaSh'
smash_dir = expanduser('~/.smash')
smashlib_dir = os.path.dirname(os.path.dirname(__file__))
canonical_prof = os.path.join(smashlib_dir, 'ipython_config.py')
canonical_user_prof = os.path.join(smashlib_dir, 'user_config.py')

def main():
    from smashlib import embed
    from IPython.core.profiledir import ProfileDir
    #profile_dir=os.path.join(smash_dir, main_profile_name)
    #ProfileDir.create_profile_dir(profile_dir)
    if not os.path.exists(smash_dir):
        os.mkdir(smash_dir)
    ProfileDir.create_profile_dir_by_name(smash_dir, main_profile_name)
    #ProfileDir.create_profile_dir_by_name(smash_dir, user_profile_name)
    profile_dir = os.path.join(smash_dir, 'profile_'+main_profile_name)
    config_file = os.path.join(profile_dir, 'ipython_config.py')
    shutil.copy(canonical_prof, config_file,)
    from smashlib.data import user_config
    if not os.path.exists(user_config):
        shutil.copy(canonical_user_prof, user_config)
    embed(["--profile-dir=~/.smash/profile_SmaSh",
           #'--config=~/.smash/config.py'
           ])
entry = main

if __name__=='__main__':
    try:
        from IPython import Shell
    except:
        print ("\nFATAL: cannot run SmaSh.\n"
               "  IPython lib is not available.  \n"
               "    To reproduce this error, try running:\n"
               "      /usr/bin/env python -c\"from IPython import Shell\"\n")
        sys.exit(1)
    else:
        main()

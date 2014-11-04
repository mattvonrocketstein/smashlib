#!/usr/bin/env python
#
# you would think that "env python" would work everywhere, but due
# due to interaction with sourced venv's this is actually a tricky
# business..
import os, sys

expanduser = os.path.expanduser

def main():
    """ essentially this is like calling smashlib.util.embed(), but,
        we might not actually be able to import smashlib yet so we'll
        have to reproduce some of the effort.
    """
    _smashlib, _smashplugins = (expanduser('~/.smash/'),
                                expanduser('~/.smash/plugins'))
    #for p in [_smashlib,_smashplugins]:
    #    if p not in sys.path:
    #        sys.path.append(p)
    #import smashlib
    from smashlib import embed
    embed()
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

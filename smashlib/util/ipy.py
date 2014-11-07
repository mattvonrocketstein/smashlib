""" smashlib.util.ipy

    import shortcuts for ipython.  this also might help to keep
    smashlib in sync with changing ipython target versions?
"""
from IPython.utils.coloransi import TermColors

class Reporter(object):

    verbose = False

    def report(self, msg, *args, **kargs):
        force = kargs.pop('force', False)
        if self.verbose or force:
            print "{0}: {1} {2}".format(
                TermColors.Blue + self.__class__.__name__,
                TermColors.Red + msg,
                TermColors.Normal
                )
            if args:
                print '  ',args

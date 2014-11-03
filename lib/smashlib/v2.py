""" smashlib.v2
"""

from IPython.config.configurable import Configurable
from IPython.utils.coloransi import TermColors
from IPython.utils.traitlets import Bool
from IPython.utils.traitlets import EventfulList, EventfulDict

class EventfulMix(object):

    def _init_elist(self, name, elist):
        insert_name = '_event_insert_'+name
        set_name = '_event_set_'+name
        del_name = '_event_del_'+name
        kls_name = self.__class__.__name__
        def default_insert(new):
            self.report('hooks add', new)
        def default_set(slice_or_index, val):
            msg = 'set (override {0}.{1})'.format(
                kls_name,set_name)
            self.report(msg, slice_or_index, val)
        def default_del(old):
            self.report('hooks del',old)
        insert_callback = getattr(self, insert_name, default_insert)
        set_callback = getattr(self, set_name, default_set)
        kargs = dict(
            insert_callback=insert_callback,
            set_callback=set_callback,
            del_callback=getattr(self,
                                 del_name,
                                 default_del
                                 ),
            reverse_callback=None,
            sort_callback=None)
        elist.on_events(**kargs)
        # finally, reassign everything so the events get called
        for i in range(len([x for x in elist])):
            elist[i] = elist[i]

    def _get_eventful_type(self, type):
        out = {}
        for name, trait in self.traits().items():
            if isinstance(trait, type):
                out[name] = getattr(self, name)
        return out

    def init_eventful(self):
        # initialize all elists.
        elists = self._get_eventful_type(EventfulList)
        for name, elist in elists.items():
            self._init_elist(name, elist)

class Base(Configurable, EventfulMix):

    def __init__(self, shell, **kargs):
        super(Base, self).__init__(config=shell.config, shell=shell)
        self.shell.configurables.append(self)
        self.report("initializing {0}".format(self))
        self.init_eventful()
        self.init()

    @property
    def smash(self):
        try:
            return self.shell._smash
        except AttributeError:
            raise Exception("load smash first")

    def init(self):
        self.report("base self.init should probably be overridden")


class Reporter(Base):
    verbose = Bool(False, config=True)
    def report(self, msg, *args):
        if self.verbose:
            print "{0}: {1} {2}".format(
                TermColors.Blue + self.__class__.__name__,
                TermColors.Red + msg,
                TermColors.Normal
                )
            if args:
                print '  ',args

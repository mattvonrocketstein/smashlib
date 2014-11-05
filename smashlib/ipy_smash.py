""" smashlib.ipy_smash

    Defines the main smash extension, which itself loads and
    allows communications between the other smash extensions.

    TODO: dynamic loading of extensions (use EventfulList)
"""
import cyrusbus

from IPython.utils.traitlets import EventfulList, List, Bool

from smashlib.v2 import Reporter
from smashlib.util.reflect import from_dotpath, ObjectNotFound
from smashlib.channels import C_POST_RUN_INPUT, C_POST_RUN_CELL, C_WARNING
from smashlib.util import receives_event

class Smash(Reporter):
    extensions = List(default_value=[], config=True)
    verbose_events = Bool(False, config=True)

    def init_extensions(self):
        record = {}
        for dotpath in self.extensions:
            mod = from_dotpath(dotpath)
            ext_name = dotpath.split('.')[-1]
            ext_obj = mod.load_ipython_extension(self.shell)
            record[ext_name] = ext_obj
            if ext_obj is None:
                msg = '{0}.load_ipython_extension should return an object'
                msg = msg.format(dotpath)
                self.publish('warning', msg)
            #self.shell.magic('load_ext {0}'.format(extension))
        self.loaded_extensions = record
        self.report("loaded extensions:", self.loaded_extensions.keys())

    def parse_argv(self):
        """ parse arguments recognized by myself,
            then let all the extensions take a stab
            at it.
        """
        args, unknown = super(Smash,self).parse_argv()
        ext_objs = self.loaded_extensions.values()
        for obj in ext_objs:
            if obj:
                args,unknown = obj.parse_argv()

    @property
    def project_manager(self):
        return self.loaded_extensions['ipy_project_manager']

    def init(self):
        self.shell._smash = self
        self.init_bus()
        self.init_extensions()
        self.parse_argv()

    def init_bus(self):
        """ note: it is a special case that due to bootstrap ordering,
            @receive_events is not possible for this class.  if you want
            to register event callbacks you'll have to register everything
            the simple way.
        """
        super(Smash,self).init_bus()
        bus = cyrusbus.Bus()
        bus.subscribe(C_WARNING, self.warning)
        bus.subscribe(C_POST_RUN_INPUT, self.input_finished_hook)
        self.bus = bus

    def input_finished_hook(self, bus, raw_finished_input):
        if not raw_finished_input.strip():
            return

        rehash_if = [
            'python setup.py develop',
            'python setup.py install',
            'apt-get install']
        for x in rehash_if:
            if x in raw_finished_input:
                self.report("detected possible $PATH changes (rehashing)")
                self.shell.magic('rehashx')

    def warning(self, bus, *args, **kwargs):
        msg, rest = args[0], args[1:]
        self.report("WARNING: "+msg, *rest, force=True)

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    ip._smash = Smash(ip)
    return ip._smash

def unload_ipython_extension(ip):
    del ip._smash

""" smashlib.ipy_smash

    Defines the main smash extension, which itself loads and allows
    communications between the other smash extensions.
"""
import cyrusbus

from smashlib.v2 import Reporter
from smashlib.util.reflect import from_dotpath, ObjectNotFound

from IPython.utils.traitlets import EventfulList

class Smash(Reporter):
    require_extensisons = [
        'smashlib.ipy_cd_hooks',
        'smashlib.ipy_venv',
        'smashlib.ipy_project_manager',
        'smashlib.ipy_liquidprompt',
        ]

    def init_extensions(self):
        record = {}
        for dotpath in self.require_extensisons:
            mod = from_dotpath(dotpath)
            ext_name = dotpath.split('.')[-1]
            record[ext_name] = mod.load_ipython_extension(self.shell)
            #self.shell.magic('load_ext {0}'.format(extension))
        self.extensions = record

    @property
    def project_manager(self):
        return self.extensions['ipy_project_manager']

    def init(self):
        self.shell._smash = self
        self.init_bus()
        self.init_extensions()

    def warning(self, bus, *args, **kwargs):
        msg, rest = args[0], args[1:]
        self.report("WARNING: "+msg, *rest, force=True)

    def init_bus(self):
        bus = cyrusbus.Bus()
        bus.subscribe('warning', self.warning)
        self.bus = bus

        """
        bus.subscribe('post_invoke',     _verbose('post_invoke'))
        bus.subscribe('pre_invoke',      _verbose('pre_invoke'))
        bus.subscribe('pre_activate',    _verbose('pre_activate'))
        bus.subscribe('post_activate',   _verbose('post_activate'))
        bus.subscribe('pre_deactivate',  _verbose('pre_deactivate'))
        bus.subscribe('post_deactivate', _verbose('post_deactivate'))
        """

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    ip._smash = Smash(ip)


def unload_ipython_extension(ip):
    del ip._smash

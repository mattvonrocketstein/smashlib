""" smashlib.ipy_cd_hooks

"""
import os

from smashlib.v2 import Reporter
from smashlib.util.reflect import from_dotpath, ObjectNotFound

from IPython.utils.traitlets import EventfulList
from IPython.core.magics.osm import OSMagics
CD_EVENT = 'cd'


class ChangeDirHooks(Reporter):

    last_dir = None
    change_dir_hooks = EventfulList(default_value=[], config=True)
    original_cd_magic = OSMagics.cd

    @staticmethod
    def test_change_message(bus, new, old):
        """ used as a demo in user_config.py """
        print 'test_change_message got "cd" event:', dict(new=new, old=old)

    def init(self):
        self.init_patches()

    def init_patches(self):
        shell = self.shell
        # FIXME: reregister it properly instead of patching it
        if not getattr(self, '_already_patched', False):
            def mycd(parameter_s=''):
                #self.report('executing patched cd on {0}'.format(parameter_s))
                try:
                    self.original_cd_magic(parameter_s+ '-q')
                except Exception as e:
                    self.report("error with cd.")
                    raise
                else:
                    this_dir = self.smash.system('pwd', quiet=True)
                    self.smash.bus.publish(CD_EVENT, this_dir, self.last_dir)
                    os.environ['PWD'] = this_dir
                    self.last_dir = this_dir

            #self.original_cd_magic = shell.magics_manager.magics['line']['cd']

            self.original_cd_magic = OSMagics
            self.shell.magics_manager.magics['line']['cd'] = mycd
            self._already_patched = True
            self.report("finished patching cd magic")
        else:
            self.report("cd magic is already patched")

    def _event_set_change_dir_hooks(self, slice_or_index, val):
        try:
            obj = from_dotpath(val)
        except ObjectNotFound as e:
            err = 'ChangeDirHooks.change_dir_hooks: '
            raise ObjectNotFound(err+e.message)
        self.report("retrieved from dotpath: ", obj)
        self.report("object will be subscribed to <{0}>".format(CD_EVENT))
        self.smash.bus.subscribe(CD_EVENT, obj)

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    return ChangeDirHooks(ip)

def unload_ipython_extension(ip):
    original = ChangeDirHooks.original_cd_magic
    assert original is not None
    ip.shell.magics_manager.magics['line']['cd'] = original

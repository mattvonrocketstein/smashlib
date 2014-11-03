"""
"""
import os, sys, glob
from smashlib.v2 import Reporter
from smashlib.python import opj
from smashlib.util import truncate_fpath
from IPython.core.magic import Magics, magics_class, line_magic
from smashlib.venv import get_venv, is_venv, to_vbin, to_vlib, get_path

@magics_class
class VirtualEnvMagics(Magics, ):
    @line_magic
    def venv_activate(self, parameter_s=''):
        self.report("magic venv_activate", parameter_s)
        self.vext._activate_str(parameter_s)

    @property
    def report(self):
        return self.vext.report

def current_project():
    return 'cproject-niy'

# channel names for use with the smash bus
C_POST_ACTIVATE = 'post_activate_venv'
C_PRE_ACTIVATE = 'pre_activate_venv'
C_POST_DEACTIVATE = 'post_deactivate_venv'
C_PRE_DEACTIVATE = 'pre_deactivate'

class VirtualEnvSupport(Reporter):

    def init(self):
        self.smash.bus.subscribe(
            C_POST_ACTIVATE, self.channel_post_activate)

    def channel_post_activate(self, bus, venv_dir):
        self.report("!post-activate: "+venv_dir)

    def deactivate(self):
        self.smash.bus.publish(
            C_PRE_DEACTIVATE,
            name = current_project())
        try:
            venv = get_venv()
        except KeyError:
            return False
        else:
            if not os.path.exists(venv):
                err = 'refusing to deactivate (relocated?) venv'
                raise RuntimeError(err)

            del os.environ['VIRTUAL_ENV']
            path = get_path()
            path = path.split(':')

            # clean $PATH according to bash..
            # TODO: also rehash?
            vbin = to_vbin(venv)
            if vbin in path:
                msg = 'removing old venv bin from PATH: ' + \
                      truncate_fpath(str(vbin))
                self.report(msg)
                path.remove(vbin)
                os.environ['PATH'] = ':'.join(path)

            # clean sys.path according to python..
            # stupid, but this seems to work
            self.report('cleaning sys.path')
            new_path = []
            for entry in sys.path:
                if entry and not entry.startswith(venv):
                    new_path.append(entry)
                else:
                    self.warning("ignoring special-case?")
                    #if entry.startswith(smashlib._meta['smash_home']) and \
                    #   'IPython' in entry:
                        # careful, dont remove our own bootstraps.
                        # specifically this will break --project=..
                        # invocation
                    #    new_path.append(entry)
                    #else:
                        #print 'cleaning: ',entry
                    #    pass

            sys.path = new_path
            # TODO: clean sys.modules?
            self.smash.bus.publish(
                C_POST_DEACTIVATE,
                #name=Project('__smash__').CURRENT_PROJECT)
                name=current_project())
            return True

    def _activate_str(self, obj):
        absfpath = os.path.abspath(os.path.expanduser(obj))
        self.smash.bus.publish(C_PRE_ACTIVATE, name=absfpath)
        if True:
            vbin = to_vbin(absfpath)
            vlib = to_vlib(absfpath)

            # compute e.g. <venv>/lib/python2.6.
            # we call bullshit if they have a more than one dir;
            # it might be a chroot but i dont think it's a venv
            python_dir = glob.glob(opj(vlib, 'python*/'))
            if not 0 < len(python_dir) < 2:
                err = ('Not sure how to handle this; '
                       'zero or 1+ dirs matching "python*"')
                raise RuntimeError, err
            python_dir = python_dir[0]

            # this bit enables switching between two venv's
            # that might be "no-global-site" vs "use-global-site"
            site_file = opj(python_dir, 'site.py')
            assert os.path.exists(site_file)
            tmp = dict(__file__=site_file)
            execfile(site_file, tmp)
            tmp['main']()

            # some environment variable manipulation that would
            # normally be done by 'source bin/activate', but is
            # not handled by activate_this.py
            path = get_path().split(':')
            os.environ['PATH'] = ':'.join([vbin] + path)
            os.environ['VIRTUAL_ENV'] = absfpath
            self.report('adding "%s" to PATH; rehashing aliases' % truncate_fpath(vbin))
            sandbox = dict(__file__ = opj(vbin, 'activate_this.py'))
            execfile(opj(vbin, 'activate_this.py'), sandbox)

            # libraries like 'datetime' can fail on import if this isnt done,
            # i'm not sure why activate_this.py doesnt accomplish it.
            dynload = opj(python_dir, 'lib-dynload')
            sys.path.append(dynload)

            # NB: this updates bins but kills other aliases!
            self.shell.magic('rehashx')
            self.smash.bus.publish(C_POST_ACTIVATE, name=absfpath)

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    venv = VirtualEnvSupport(ip)
    VirtualEnvMagics.vext = venv
    ip.register_magics(VirtualEnvMagics)
    return venv


def unload_ipython_extension(ip):
    """undo magic here.."""

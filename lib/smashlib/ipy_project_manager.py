""" ipy_project_manager

    Defines the project manager extension.  Features:

"""
import os
from IPython.config.configurable import SingletonConfigurable
from IPython.utils.traitlets import Int, Float, Unicode, Bool
from IPython.utils.traitlets import EventfulDict, EventfulList
from IPython.utils.traitlets import Instance
from IPython.core.magic import Magics, magics_class, line_magic
from smashlib.util.venv import contains_venv, is_venv
from smashlib.v2 import Reporter
from smashlib.ipy_liquidprompt import C_UPDATE_PROMPT_REQUEST
def clean_project_name(name):
    return name.replace('-','_').replace('.', '_')

class UnknownProject(Exception):
    pass

@magics_class
class ProjectMagics(Magics, ):
    @line_magic
    def activate(self, parameter_s=''):
        parts = parameter_s.split()
        self.pm.activate_project(parameter_s)
    @line_magic
    def jump(self, parameter_s=''):
        parts = parameter_s.split()
        self.pm.jump(parameter_s)

class ProjectManager(Reporter):
    config_file    = Unicode(u'', config=True)
    search_dirs    = EventfulList(default_value=[], config=True)
    project_map    = EventfulDict(default_value={}, config=True)
    alias_map      = EventfulDict(default_value={}, config=True)
    activation_map = EventfulDict(default_value={}, config=True)
    venv_map       = EventfulDict(default_value={}, config=True)

    def init(self):
        from smashlib.ipy_cd_hooks import CHANNEL
        self.smash.bus.subscribe(CHANNEL, self.cd_hook)

    def cd_hook(self, bus, new_dir, *args, **kargs):
        if new_dir in self.project_map.values():
            self.report("this directory is a project.")

    def _event_set_search_dirs(self, slice_or_index, val):
        val = os.path.abspath(os.path.expanduser(val))
        if not os.path.exists(val):
            self.report("warning: new search_dir doesnt exist: {0}".format(val))
        else:
            contents = os.listdir(unicode(val))
            bind_list = []
            for name in contents:
                clean_name = clean_project_name(name)
                path = os.path.join(val, name)
                if name not in self.project_map:
                    bind_list.append(path)
                    self.project_map[clean_name] = path
            self.report("discovered {0} projects under '{1}'".format(
                len(bind_list), val))
        self.update_pmi()

    def _get_prop(self, name, path):
        def fxn(himself):
            self.activate_project(name)
        out = property(fxn)
        return out

    def update_pmi(self):
        for name, path in self.project_map.items():
            prop = self._get_prop(name, path)
            setattr(ProjectManagerInterface, name, prop)

    def _require_project(self, name):
        if name not in self.project_map:
            raise UnknownProject(name)

    def jump(self, name):
        self._require_project(name)
        _dir = os.path.expanduser(self.project_map[name])
        if not os.path.exists(_dir):
            self.report("Not found: {0}".format(_dir))
        else:
            self.shell.magic('pushd {0}'.format(_dir))

    def build_argparser(self):
        parser = super(ProjectManager, self).build_argparser()
        parser.add_argument('--project', default='')
        return parser

    def parse_argv(self):
        args, unknown = super(ProjectManager,self).parse_argv()
        if args.project:
            try:
                self.activate_project(args.project)
            except UnknownProject:
                msg = 'unknown project: {0}'.format(args.project)
                self.publish('warning', msg)
        return args, unknown

    def activate_project(self, name):

        def guess_activation_steps(dir):
            found_venv = None
            default_venv_dir = self.venv_map.get(name, None)
            if default_venv_dir:
                default_venv = contains_venv(default_venv_dir,
                                             report=self.report)
                if not default_venv:
                    msg = ("ProjectManager.venv_map uses {0}, "
                           "but no venv was found")
                    msg = msg.format(default_venv_dir)
                    self.publish('warning', msg)
                else:
                    found_venv = default_venv
            else:
                found_venv = contains_venv(dir, report=self.report)

            if found_venv:
                self.shell.magic('venv_activate {0}'.format(found_venv))
                return True
            else:
                msg = "no activation steps are understood for {0}".format(name)
                self.report(msg)

        self._require_project(name)
        _dir = self.project_map[name]
        activation_steps = self.activation_map.get(
            name, [])
        if not activation_steps:
            activation_steps = guess_activation_steps(_dir)

        if not os.getcwd()==self.project_map[name]:
            self.jump(name)
        # fixme: this should really just be
        # called from a post-input hook
        self.publish(C_UPDATE_PROMPT_REQUEST, self)
class ProjectManagerInterface(object):
    pass
pmi = ProjectManagerInterface()

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    ProjectManager.pmi = pmi
    pm = ProjectManager(ip)
    #pmi.pm = pm

    ip.user_ns['proj'] = pmi
    ProjectMagics.pm = pm
    ip.register_magics(ProjectMagics)
    return pm

def unload_ipython_extension(ip):
    """ called by %unload_ext magic"""
    print 'not implemented yet'

#!/usr/bin/env python
"""
IPython extension to fix pysh profile
"""
import os
from IPython.config.configurable import SingletonConfigurable
from IPython.utils.traitlets import Int, Float, Unicode, Bool
from IPython.utils.traitlets import EventfulDict, EventfulList
from IPython.utils.traitlets import Instance
from IPython.core.magic import Magics, magics_class, line_magic
from .v2 import Reporter

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
                path = os.path.join(val, name)
                if name not in self.project_map:
                    bind_list.append(path)
                    self.project_map[name.replace('-','_')] = path
            self.report("discovered {0} projects under '{1}'".format(
                len(bind_list), val))

    def _require_project(self, name):
        err = 'unknown project {0}'.format(name)
        assert name in self.project_map, err

    def jump(self, name):
        self._require_project(name)
        _dir = os.path.expanduser(self.project_map[name])
        if not os.path.exists(_dir):
            self.report("Not found: {0}".format(_dir))
        else:
            self.shell.magic('pushd {0}'.format(_dir))

    def activate_project(self, name):
        from smashlib.venv import is_venv, contains_venv
        def guess_activation_steps(dir):
            default_venv = self.smash.project_manager.venv_map.get(name, None)
            found_venv = default_venv or \
                         is_venv(dir) or \
                         contains_venv(dir, report=self.report)
            if found_venv:
                self.shell.magic('venv_activate {0}'.format(dir))
                return True
        self._require_project(name)
        _dir = self.project_map[name]
        activation_steps = self.activation_map.get(
            name, [])
        if not activation_steps:
            activation_steps = guess_activation_steps(_dir)
            if activation_steps:
                self.report("guessed activation-steps: ", activation_steps)
            else:
                msg = "no activation steps are understood for {0}".format(name)
                self.report(msg)

        if not os.getcwd()==self.project_map[name]:
            self.jump(name)

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    pm=ProjectManager(ip)
    #ip.user_ns['proj'] = pm
    ProjectMagics.pm = pm
    ip.register_magics(ProjectMagics)
    return pm

def unload_ipython_extension(ip):
    """ called by %unload_ext magic"""
    pass

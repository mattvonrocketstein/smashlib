""" smashlib.project_manager
"""
import os

from IPython.utils.traitlets import EventfulDict, EventfulList

from smashlib.ipy_cd_hooks import CD_EVENT

from smashlib.v2 import Reporter
from smashlib.util import guess_dir_type
from smashlib.util.events import receives_event
from smashlib.util import truncate_fpath
from smashlib.python import abspath, expanduser
from smashlib.util.venv import contains_venv
from smashlib.project_manager.util import (
    clean_project_name, UnknownProjectError)
from smashlib.util.ipy import green

class ProjectManager(Reporter):
    search_dirs    = EventfulList(default_value=[], config=True)
    project_map    = EventfulDict(default_value={}, config=True)
    alias_map      = EventfulDict(default_value={}, config=True)
    activation_map = EventfulDict(default_value={}, config=True)
    venv_map       = EventfulDict(default_value={}, config=True)

    _current_project = None

    @property
    def reverse_project_map(self):
        return dict([[v,k] for k,v in self.project_map.items()])

    @receives_event(CD_EVENT)
    def cd_hook(self, new_dir, old_dir):
        if new_dir in self.project_map.values():
            project_name = self.reverse_project_map[new_dir]
            _help='this directory is a project.  to activate it, type {0}'
            _help = _help.format(green('proj.'+project_name))
            self.info(_help)

    def init(self):
        # at this point project_map has been created from
        # configuration data, but it's callback mechanism
        # which does validation has not be registered yet.
        # bind it, then reinitialize project_map to fix
        # up and then bind any data set so far
        self.project_map.on_set(self._event_set_project_map)
        for x in self.project_map.copy():
            self.project_map[x]=self.project_map[x]

    def _event_set_project_map(self, key, val):
        """ final word in cleaning/verifying/binding
            input that goes to project_map.  project_map
            should have only pristine data. Therefore DO
            NOT abstract the helper method "_bind_project".
        """
        def _bind_project(name, path):
            """ NOTE: be aware this is also used for re-binding """
            if not os.path.exists(path):
                self.report("bound project {0} to nonexistent {1}".format(
                    name, path))
            self.update_interface()
        name = key
        clean_name = clean_project_name(name)
        clean_path = abspath(expanduser(val))
        dict.__setitem__(
            self.project_map,
            clean_name,
            clean_path)
        _bind_project(clean_name, clean_path)


    def _event_set_search_dirs(self, slice_or_index, base_dir):
        base_dir = os.path.abspath(os.path.expanduser(base_dir))
        if not os.path.exists(base_dir):
            msg = "new search_dir doesnt exist: {0}"
            self.warning(msg.format(base_dir))
        else:
            contents = os.listdir(unicode(base_dir))
            bind_list = []
            for name in contents:
                if name.startswith('.'):
                    self.warning("skipping "+name)
                path = os.path.join(base_dir, name)
                #raise Exception,path
                self.project_map[name] = path
            self.report("discovered {0} projects under '{1}'".format(
                len(bind_list), base_dir))
        self.update_interface()


    def update_interface(self):
        """ so that tab-completion works on any bound projects, the
            properties on ProjectManagerInterface (aka user_ns['proj'])
            will be updated
        """
        def _get_prop(name, path):
            def fxn(himself):
                self.activate_project(name)
            out = property(fxn)
            return out
        for name, path in self.project_map.items():
            prop = _get_prop(name, path)
            setattr(ProjectManagerInterface, name, prop)

    def _require_project(self, name):
        if name not in self.project_map:
            raise UnknownProjectError(name)

    def jump_project(self, name):
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
            except UnknownProjectError:
                msg = 'unknown project: {0}'.format(args.project)
                self.warning(msg)
        return args, unknown

    def _guess_activation_steps(self, name, dir):
        found_venv = None
        default_venv_dir = self.venv_map.get(name, None)
        if default_venv_dir:
            default_venv = contains_venv(default_venv_dir,
                                         report=self.report)
            if not default_venv:
                msg = ("ProjectManager.venv_map uses {0}, "
                       "but no venv was found")
                msg = msg.format(default_venv_dir)
                self.warning(msg)
            else:
                found_venv = default_venv
                self.report("venv_map specifies to use {0}".format(
                    truncate_fpath(found_venv)))
        else:
            found_venv = contains_venv(dir, report=self.report)

        if found_venv:
            self.shell.magic('venv_activate {0}'.format(found_venv))
            return True
        else:
            msg = "no activation steps are understood for {0}".format(name)
            self.report(msg)
        self._current_project = name

    def _guess_deactivation_steps(self, name, _dir):
        self.shell.magic('venv_deactivate')

    def deactivate(self):
        name = self._current_project
        if name is None:
            return
        self._require_project(name)
        _dir = self.project_map[name]
        self.report("deactivating: "+name)
        deactivation_steps = [] #self.deactivation_map.get(name, [])
        if not deactivation_steps:
            activation_steps = self._guess_deactivation_steps(name, _dir)
        self._current_project = None

    def activate_project(self, name):
        self.deactivate()
        self.report("activating: "+name)
        self._require_project(name)
        _dir = self.project_map[name]
        activation_steps = self.activation_map.get(
            name, [])
        if not activation_steps:
            activation_steps = self._guess_activation_steps(name, _dir)

        if not os.getcwd()==self.project_map[name]:
            self.jump_project(name)
        self._current_project = name

    def guess_project_type(self, project_name):
        pdir = self.project_map[project_name]
        return guess_dir_type(pdir)

    def _lint_python(self, pdir):
        """ """
        from smashlib.util.linter import PyLinter
        cmd_exec = self.smash.system
        linter = PyLinter(cmd_exec=self.smash.system,)
        linter(pdir)

    def init_pmi(self, pmi):
        ProjectManagerInterface._project_manager = self
        self.smash.shell.user_ns['proj'] = pmi

class ProjectManagerInterface(object):
    """ This object should be a singleton and will be assigned to
        that main namespace as "proj".  In addition to the methods
        you see below, The ProjectManager extension
        will dynamically add/remove properties on to this
    """
    _project_manager = None

    @property
    def _type(self):
        return self._project_manager.guess_project_type(
            self._project_manager._current_project)

    @property
    def _venvs(self):
        from smashlib.util.venv import find_venvs
        return find_venvs(
            self._project_managerproject_map[self._project_manager_current_project])


    def _ack(self, pat):
        """ TODO: should really be some kind of magic """
        venvs = self._venvs
        cmd = 'ack "{0}" "{1"} {2}'
        pdir = self._project_manager.project_map[
            self._project_manager._current_project]
        ignores = ['--ignore-dir="{0}"'.format(venv) for venv in venvs]
        ignores = ' '.join(ignores)
        cmd = cmd.format(pat, pdir,ignores)
        self._project_managersmash.system(cmd)

    @property
    def _lint(self):
        pm = self._project_manager
        project_name = pm._current_project
        if project_name is None:
            pm.report("No project has been selected.")
            return

        project_types = self._type
        lint_fxns = [ getattr(pm,'_lint_'+ptype, None) \
                      for ptype in project_types ]
        lint_fxns = filter(None,lint_fxns)
        if not lint_fxns:
            msg = "no linters found for project-type: "+str(project_types)
            pm.report(msg)
        else:
            out = [ lint_fxn(pm.project_map[project_name]) \
                    for  lint_fxn in lint_fxns ]

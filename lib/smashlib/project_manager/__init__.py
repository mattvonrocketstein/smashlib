""" smashlib.project_manager
"""
import os
from IPython.utils.traitlets import Unicode
from IPython.utils.traitlets import EventfulDict, EventfulList
from IPython.utils.traitlets import Instance
from IPython.core.magic import Magics, magics_class, line_magic

from smashlib.ipy_cd_hooks import CD_EVENT
from smashlib.ipy_liquidprompt import C_UPDATE_PROMPT_REQUEST

from smashlib.v2 import Reporter
from smashlib.util import receives_event
from smashlib.util import truncate_fpath
from smashlib.python import abspath, expanduser
from smashlib.util.venv import contains_venv
from smashlib.project_manager.util import (
    clean_project_name, UnknownProjectError)

@magics_class
class ProjectMagics(Magics):
    @line_magic
    def activate(self, parameter_s=''):
        self.pm.activate_project(parameter_s)

    @line_magic
    def add_project(self, parameter_s=''):
        name = parameter_s.split()[0]
        path=parameter_s[len(name)+1:]
        print 'would have added project_map[{0}]={1}'.format(name,path)
        #self.pm.project_map[name]=path

    @line_magic
    def jump(self, parameter_s=''):
        self.pm.jump_project(parameter_s)

class ProjectManager(Reporter):
    config_file    = Unicode(u'', config=True) # not used
    search_dirs    = EventfulList(default_value=[], config=True)
    project_map    = EventfulDict(default_value={}, config=True)
    alias_map      = EventfulDict(default_value={}, config=True)
    activation_map = EventfulDict(default_value={}, config=True)
    venv_map       = EventfulDict(default_value={}, config=True)

    @receives_event(CD_EVENT)
    def cd_hook(self, new_dir, old_dir):
        if new_dir in self.project_map.values():
            self.report("this directory is a project.")

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
            self.update_pmi()
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
            msg = "warning: new search_dir doesnt exist: {0}"
            msg = msg.format(base_dir)
            self.report(msg)
        else:
            contents = os.listdir(unicode(base_dir))
            bind_list = []
            for name in contents:
                path = os.path.join(base_dir, name)
                #raise Exception,path
                self.project_map[name] = path
            self.report("discovered {0} projects under '{1}'".format(
                len(bind_list), base_dir))
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

        self._require_project(name)
        _dir = self.project_map[name]
        activation_steps = self.activation_map.get(
            name, [])
        if not activation_steps:
            activation_steps = guess_activation_steps(_dir)

        if not os.getcwd()==self.project_map[name]:
            self.jump_project(name)
        # fixme: this should really just be
        # called from a post-input hook
        self.publish(C_UPDATE_PROMPT_REQUEST,
                     self.__class__.__name__)

class ProjectManagerInterface(object):
    """ This object should be a singleton and will be assigned to
        that main namespace as "proj".  In addition to the methods
        you see below, The ProjectManager extension
        will dynamically add/remove properties on to this
    """
    pass

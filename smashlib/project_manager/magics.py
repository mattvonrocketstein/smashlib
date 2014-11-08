""" smashlib.project_manager.magics
"""
from IPython.core.magic import Magics, magics_class, line_magic

@magics_class
class ProjectMagics(Magics):
    @line_magic
    def activate(self, parameter_s=''):
        self.project_manager.activate_project(parameter_s)

    @line_magic
    def add_project(self, parameter_s=''):
        name = parameter_s.split()[0]
        path = parameter_s[len(name)+1:]
        self.project_manager.project_map[name]=path

    @line_magic
    def jump(self, parameter_s=''):
        self.project_manager.jump_project(parameter_s)

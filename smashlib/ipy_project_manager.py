""" ipy_project_manager

    Defines the project manager extension.  Features:

"""
from smashlib.project_manager import (
    ProjectMagics, ProjectManager, ProjectManagerInterface)

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    pmi = ProjectManagerInterface()
    ProjectManager.interface = pmi
    pm = ProjectManager(ip)
    pm.init_pmi(pmi)

    ProjectMagics.project_manager = pm
    ip.register_magics(ProjectMagics)
    return pm

def unload_ipython_extension(ip):
    """ called by %unload_ext magic"""
    print 'not implemented yet'

""" ipy_project_manager

    Defines the project manager extension.  Features:

"""
from smashlib.project_manager import (
    ProjectMagics, ProjectManager, ProjectManagerInterface)

def load_ipython_extension(ip):
    """ called by %load_ext magic"""
    ip = get_ipython()
    pmi = ProjectManagerInterface()
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

""" smashlib.util.linter
"""
import os

from collections import defaultdict
from smashlib.util._fabric import require_bin
from smashlib.util.venv import find_venvs
from smashlib.v2 import Reporter

class Linter(Reporter):
    """ """
    def __init__(self, cmd_exec=None):
        if cmd_exec==None:
            cmd_exec=os.system
        self.cmd_exec = cmd_exec
        self.init_logger()

    def __call__(self):
        raise Exception("abstract")

class PyLinter(Linter):

    verbose = True

    def __call__(self, _dir):
        require_bin('flake8')
        ignore = [
            'E501', # line-too-long
            ]
        base_cmd = 'cd {0} && flake8 {0}'
        cmd = base_cmd
        exclude = ['*build/*']
        for venv_dir in find_venvs(_dir):
            exclude.append(venv_dir)
        ignore = ','.join(ignore)
        exclude = ','.join(exclude)
        exclude = ' --exclude='+exclude
        ignore = ' --ignore='+ignore
        cmd = cmd.format(_dir) +  (exclude or '')
        output = self.cmd_exec(cmd)
        bad_files = [x.split(':')[0] for x in output.split('\n')]
        err_counter = defaultdict(lambda:0)
        for x in bad_files:
            err_counter[x] += 1
        # sort files by number of errors
        sorted_by_severity = sorted(err_counter.items(), key=lambda x:-x[1])
        top = sorted_by_severity[:3]
        report = dict(sorted_by_severity)
        print output
        self.report("total problems: {0}".format(sum(report.values())))
        self.report("top files: {0}".format(dict(top)))
        return report.keys()

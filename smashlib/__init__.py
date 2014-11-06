""" smashlib
"""

def start_ipython(argv=None, **kwargs):
    from IPython.terminal.ipapp import TerminalIPythonApp as _
    from smashlib.overrides import TerminalInteractiveShell
    class TerminalIPythonApp(_):
        @classmethod
        def launch_instance(cls, argv=None, **kwargs):
            app = cls.instance(**kwargs)
            app.initialize(argv)
            app.start()

        def init_shell(self):
            """initialize the InteractiveShell instance"""
            # Create an InteractiveShell instance.
            # shell.display_banner should always be False for the terminal
            # based app, because we call shell.show_banner() by hand below
            # so the banner shows *before* all extension loading stuff.
            self.shell = TerminalInteractiveShell.instance(parent=self,
                            display_banner=False, profile_dir=self.profile_dir,
                            ipython_dir=self.ipython_dir, user_ns=self.user_ns)
            self.shell.configurables.append(self)
    launch_new_instance = TerminalIPythonApp.launch_instance

    return launch_new_instance(argv=argv, **kwargs)

def embed(argv):
    #from IPython import start_ipython
    start_ipython(argv=argv)

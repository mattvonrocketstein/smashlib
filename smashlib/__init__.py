""" smashlib
"""
def start_ipython(argv=None, **kwargs):
    from IPython.terminal.ipapp import TerminalIPythonApp as _
    from IPython.terminal.interactiveshell import \
         TerminalInteractiveShell as tis
    class SmashTerminalInteractiveShell(tis):
        def __init__(self,*args,**kargs):
            sooper = super(SmashTerminalInteractiveShell,self)
            sooper.__init__(*args, **kargs)
            self._smash_last_input = ""
        @property
        def smash(self):
            return getattr(self, '_smash', None)

        def raw_input(self, *args, **kargs):
            sooper = super(SmashTerminalInteractiveShell,self)
            out = sooper.raw_input(*args, **kargs)
            self._smash_last_input += out
            print 'post-input'
            return out

        def run_cell(self, raw_cell, store_history=False,
                     silent=False, shell_futures=True):
            sooper = super(SmashTerminalInteractiveShell, self)
            out = sooper.run_cell(
                raw_cell, store_history=store_history,
                silent=silent, shell_futures=shell_futures)
            if self.smash is not None:
                self.smash.bus.publish(
                    C_POST_RUN_CELL,
                    self.user_ns['In'][-1].strip())
                self.smash.bus.publish(
                    C_POST_RUN_INPUT,
                    self._smash_last_input)
                self._smash_last_input = ""
    TerminalInteractiveShell=SmashTerminalInteractiveShell
    from smashlib.channels import C_POST_RUN_INPUT, C_POST_RUN_CELL
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

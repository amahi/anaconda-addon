import re

# the path to addons is in sys.path so we can import things from org_amahi_setup
from org_amahi_setup.categories.amahi_setup import AmahiCategory
from pyanaconda.ui.tui.spokes import NormalTUISpoke
from pyanaconda.ui.common import FirstbootSpokeMixIn

# Simpleline's dialog configured for use in Anaconda
from pyanaconda.ui.tui.tuiobject import Dialog, PasswordDialog

from simpleline.render.prompt import Prompt
from simpleline.render.screen import InputState
from simpleline.render.containers import ListColumnContainer
from simpleline.render.widgets import CheckboxWidget, EntryWidget

# export only the AmahiSpoke and AmahiEditSpoke classes
__all__ = ["AmahiSpoke", "AmahiEditSpoke"]

# import gettext
# _ = lambda x: gettext.ldgettext("Amahi-anaconda-plugin", x)

# will never be translated
_ = lambda x: x
N_ = lambda x: x


class AmahiSpoke(FirstbootSpokeMixIn, NormalTUISpoke):
    """
    Class for the Amahi  TUI spoke that is a subclass of NormalTUISpoke. It
    is a simple example of the basic unit for Anaconda's text user interface.
    Since it is also inherited form the FirstbootSpokeMixIn, it will also appear
    in the Initial Setup (successor of the Firstboot tool).

    :see: pyanaconda.ui.tui.TUISpoke
    :see: pyanaconda.ui.common.FirstbootSpokeMixIn
    :see: simpleline.render.widgets.Widget

    """

    ### class attributes defined by API ###

    # category this spoke belongs to
    category = AmahiCategory

    def __init__(self, data, storage, payload, instclass):
        """
        :see: simpleline.render.screen.UIScreen
        :param data: data object passed to every spoke to load/store data
                     from/to it
        :type data: pykickstart.base.BaseHandler
        :param storage: object storing storage-related information
                        (disks, partitioning, bootloader, etc.)
        :type storage: blivet.Blivet
        :param payload: object storing packaging-related information
        :type payload: pyanaconda.packaging.Payload
        :param instclass: distribution-specific information
        :type instclass: pyanaconda.installclass.BaseInstallClass

        """

        NormalTUISpoke.__init__(self, data, storage, payload, instclass)
        self.title = N_("Amahi Server Setup")
        self._entered_text = ""

    def initialize(self):
        """
        The initialize method that is called after the instance is created.
        The difference between __init__ and this method is that this may take
        a long time and thus could be called in a separated thread.

        :see: pyanaconda.ui.common.UIObject.initialize

        """

        NormalTUISpoke.initialize(self)

    def refresh(self, args=None):
        """
        The refresh method that is called every time the spoke is displayed.
        It should update the UI elements according to the contents of
        self.data.

        :see: pyanaconda.ui.common.UIObject.refresh
        :see: simpleline.render.screen.UIScreen.refresh
        :param args: optional argument that may be used when the screen is
                     scheduled
        :type args: anything

        """

        # call parent method to setup basic container with screen title set
        super().refresh(args)

        self._entered_text = self.data.addons.org_amahi_setup.text

    def apply(self):
        """
        The apply method that is called when the spoke is left. It should
        update the contents of self.data with values set in the spoke.

        """
        if len(self._entered_text) <= 5:
                                                      return
        try:
                             check_output('wget -q --spider -U "Amahi-11-Express-x86_64" "https://api.amahi.org/api2/verify/'+self._entered_text+'"', shell=True)
        except CalledProcessError:
                             self.data.addons.org_amahi_setup.complete = False
                             return

        self.data.addons.org_amahi_setup.complete = True

        self.data.addons.org_amahi_setup.text = self._entered_text

    def execute(self):
        """
        The execute method that is called when the spoke is left. It is
        supposed to do all changes to the runtime environment according to
        the values set in the spoke.

        """

        # nothing to do here
        pass

    @property
    def completed(self):
        """
        The completed property that tells whether all mandatory items on the
        spoke are set, or not. The spoke will be marked on the hub as completed
        or uncompleted according to the returned value.

        :rtype: bool

        """
        if len(self.data.addons.org_amahi_setup.text) <= 5:
                                            return 0

        if  self.data.addons.org_amahi_setup.complete:
                   return 1

        return 0


    @property
    def status(self):
        """
        The status property that is a brief string describing the state of the
        spoke. It should describe whether all values are set and if possible
        also the values themselves. The returned value will appear on the hub
        below the spoke's title.

        :rtype: str

        """

        text = self.data.addons.org_amahi_setup.text

        # If --reverse was specified in the kickstart, reverse the text
        if self.data.addons.org_amahi_setup.reverse:
            text = text[::-1]

        if text:
            return _("Text set: %s") % text
        else:
            return _("Text not set")

    def input(self, args, key):
        """
        The input method that is called by the main loop on user's input.

        :param args: optional argument that may be used when the screen is
                     scheduled
        :type args: anything
        :param key: user's input
        :type key: unicode
        :return: if the input should not be handled here, return it, otherwise
                 return InputState.PROCESSED or InputState.DISCARDED if the input was
                 processed successfully or not respectively
        :rtype: enum InputState

        """

        if key:
            self._entered_text = key

        # no other actions scheduled, apply changes
        self.apply()

        # close the current screen (remove it from the stack)
        self.close()
        return InputState.PROCESSED

    def prompt(self, args=None):
        """
        The prompt method that is called by the main loop to get the prompt
        for this screen.

        :see: simpleline.render.prompt.Prompt

        :param args: optional argument that can be passed to App.switch_screen*
                     methods
        :type args: anything
        :return: text that should be used in the prompt for the input
        :rtype: instance of simpleline.render.prompt.Prompt or None
        """

        return Prompt(_("Enter a new text or leave empty to use the old one"))


class AmahiEditSpoke(NormalTUISpoke):
    """Example class demonstrating usage of editing in TUI"""

    category = AmahiCategory

    def __init__(self, data, storage, payload, instclass):
        """
        :see: simpleline.render.screen.UIScreen
        :param data: data object passed to every spoke to load/store data
                     from/to it
        :type data: pykickstart.base.BaseHandler
        :param storage: object storing storage-related information
                        (disks, partitioning, bootloader, etc.)
        :type storage: blivet.Blivet
        :param payload: object storing packaging-related information
        :type payload: pyanaconda.packaging.Payload
        :param instclass: distribution-specific information
        :type instclass: pyanaconda.installclass.BaseInstallClass

        """

        NormalTUISpoke.__init__(self, data, storage, payload, instclass)

        self.title = N_("Amahi Server Edit")
        self._container = None
        # values for user to set
        self._checked = False
        self._unconditional_input = ""
        self._conditional_input = ""

    def refresh(self, args=None):
        """
        The refresh method that is called every time the spoke is displayed.
        It should update the UI elements according to the contents of
        self.data.

        :see: pyanaconda.ui.common.UIObject.refresh
        :see: simpleline.render.screen.UIScreen.refresh
        :param args: optional argument that may be used when the screen is
                     scheduled
        :type args: anything

        """

        super().refresh(args)
        self._container = ListColumnContainer(columns=1)

        # add ListColumnContainer to window (main window container)
        # this will automatically add numbering and will call callbacks when required
        self.window.add(self._container)

        self._container.add(CheckboxWidget(title="Simple checkbox", completed=self._checked),
                            callback=self._checkbox_called)
        self._container.add(EntryWidget(title="Unconditional input",
                                        value=self._unconditional_input),
                            callback=self._get_unconditional_input)

        # show conditional input only if the checkbox is checked
        if self._checked:
            self._container.add(EntryWidget(title="Conditional input",
                                            value="Password set" if self._conditional_input
                                                  else ""),
                                callback=self._get_conditional_input)

        self._window.add_separator()

    def _checkbox_called(self, data):
        """Callback when user wants to switch checkbox.

        :param data: can be passed when adding callback in container (not used here)
        :type data: anything
        """

        self._checked = not self._checked

    def _get_unconditional_input(self, data):
        """Callback when user wants to set unconditional input.

        :param data: can be passed when adding callback in container (not used here)
        :type data: anything
        """

        dialog = Dialog("Unconditional input", conditions=[self._check_user_input])

        self._unconditional_input = dialog.run()

    def _get_conditional_input(self, data):
        """Callback when user wants to set conditional input.

        :param data: can be passed when adding callback in container (not used here)
        :type data: anything
        """

        # password policy for setting root password
        password_policy = self.data.anaconda.pwpolicy.get_policy("root", fallback_to_default=True)
        dialog = PasswordDialog("Unconditional input", policy=password_policy)

        self._conditional_input = dialog.run()

    def _check_user_input(self, user_input, report_func):
        """Check if user has wrote a valid value.

        :param user_input: user input for validation
        :type user_input: str

        :param report_func: function for reporting errors on user input
        :type report_func: func with one param
        """

        if re.match(r'^\w+$', user_input):
            return True
        else:
            report_func("You must set a one word")
            return False

    def input(self, args, key):
        """
        The input method that is called by the main loop on user's input.

        :param args: optional argument that may be used when the screen is
                     scheduled
        :type args: anything
        :param key: user's input
        :type key: unicode
        :return: if the input should not be handled here, return it, otherwise
                 return InputState.PROCESSED or InputState.DISCARDED if the input was
                 processed successfully or not respectively
        :rtype: enum InputState

        """

        if self._container.process_user_input(key):
            # redraw or close must be called before PROCESSED
            self.redraw()
            return InputState.PROCESSED
        else:
            return super().input(args=args, key=key)

    @property
    def completed(self):
        # completed if user entered something non-empty to the Conditioned input
        return bool(self._conditional_input)

    @property
    def status(self):
        return "Hidden input %s" % ("entered" if self._conditional_input
                                    else "not entered")

    def apply(self):

        # nothing to do here
        pass

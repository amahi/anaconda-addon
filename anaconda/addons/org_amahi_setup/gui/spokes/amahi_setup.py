from org_amahi_setup.categories.amahi_setup import AmahiCategory
from subprocess import check_output
from subprocess import call
from ipaddress import IPv4Network
from subprocess import CalledProcessError
from pyanaconda.ui.gui import GUIObject
from pyanaconda.ui.gui.spokes import NormalSpoke
from pyanaconda.ui.common import FirstbootSpokeMixIn

# export only the spoke, no helper functions, classes or constants
__all__ = ["HelloWorldSpoke"]

# import gettext
# _ = lambda x: gettext.ldgettext("hello-world-anaconda-plugin", x)

# will never be translated
_ = lambda x: x
N_ = lambda x: x


def check_credentials(username, password):
        """
        check amahi username/password
        """

        return True

def check_user_input(username,password,domain):
        import re
        
        #check domain name proper or not
        m = re.search('^((https?|ftp|smtp):\/\/)?(www.)?[a-z0-9]+\.[a-z]+(\/[a-zA-Z0-9#]+\/?)*$',domain) 
        #check if any field empty
        if len(username) == 0:
                                                      return False
        if len(password) == 0:
                                                      return False
        if (len(domain) == 0):
                                                      return False
        
        #checking domain
        try:
             m.group(0)
        except AttributeError:
                              return False
        return True

def ip_splitter():
            route = check_output("ip route | grep default", shell=True)
            each_word = route.split(b' ')
            for ip in each_word:
                          try:
                               parts = ip.split(b'.')
                               if (len(parts) == 4) and all(0 <= int(part) < 256 for part in parts):
                                                                         return parts
                          except ValueError:
                                          continue
                          except (AttributeError, TypeError):
                                          continue

def ip_getter(parts):
                         network = IPv4Network(parts[0].decode("utf-8")+'.'+parts[1].decode("utf-8")+'.'+parts[2].decode("utf-8") +'.0/24')
                         hosts_iterator = (host for host in network.hosts())
                         for host in hosts_iterator:
                                          response = call("ping -c 1 " + str(host), shell=True)
                                          if response != 0:
                                                         return str(host).split('.')

def apikey_getter(username, password, domain, ip_address):
                                 return "dfsdf"

def create_system_configuration_amahi(username, domain, ip_address, apikey, gateway):
                                                    call("sed -i 's/#apikey/"+apikey+"/' /usr/share/anaconda/addons/org_amahi_setup/system_configuration_amahi", shell=True)
                                                    call("sed -i 's/#nick/"+username+"/' /usr/share/anaconda/addons/org_amahi_setup/system_configuration_amahi", shell=True)
                                                    call("sed -i 's/#domain/"+domain+"/' /usr/share/anaconda/addons/org_amahi_setup/system_configuration_amahi", shell=True)
                                                    call("sed -i 's/#net_point/"+ip_address[0]+"."+ip_address[1]+"."+ip_address[2]+"/' /usr/share/anaconda/addons/org_amahi_setup/system_configuration_amahi", shell=True)
                                                    call("sed -i 's/#self-address/"+ip_address[3]+"/' /usr/share/anaconda/addons/org_amahi_setup/system_configuration_amahi", shell=True)
                                                    call("sed -i 's/#gateway/"+gateway+"/' /usr/share/anaconda/addons/org_amahi_setup/system_configuration_amahi", shell=True)

class HelloWorldSpoke(FirstbootSpokeMixIn, NormalSpoke):
    """
    Class for the Hello world spoke. This spoke will be in the Hello world
    category and thus on the Summary hub. It is a very simple example of a unit
    for the Anaconda's graphical user interface. Since it is also inherited form
    the FirstbootSpokeMixIn, it will also appear in the Initial Setup (successor
    of the Firstboot tool).


    :see: pyanaconda.ui.common.UIObject
    :see: pyanaconda.ui.common.Spoke
    :see: pyanaconda.ui.gui.GUIObject
    :see: pyanaconda.ui.common.FirstbootSpokeMixIn
    :see: pyanaconda.ui.gui.spokes.NormalSpoke

    """

    ### class attributes defined by API ###

    # list all top-level objects from the .glade file that should be exposed
    # to the spoke or leave empty to extract everything
    builderObjects = ["helloWorldSpokeWindow", "buttonImage"]

    # the name of the main window widget
    mainWidgetName = "helloWorldSpokeWindow"

    # name of the .glade file in the same directory as this source
    uiFile = "amahi_setup.glade"

    # category this spoke belongs to
    category = AmahiCategory

    # spoke icon (will be displayed on the hub)
    # preferred are the -symbolic icons as these are used in Anaconda's spokes
    icon = "amahi-dice"

    # title of the spoke (will be displayed on the hub)
    title = N_("_AMAHI SERVER SETUP")

    ### methods defined by API ###
    def __init__(self, data, storage, payload, instclass):
        """
        :see: pyanaconda.ui.common.Spoke.__init__
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

        NormalSpoke.__init__(self, data, storage, payload, instclass)

    def initialize(self):
        """
        The initialize method that is called after the instance is created.
        The difference between __init__ and this method is that this may take
        a long time and thus could be called in a separated thread.

        :see: pyanaconda.ui.common.UIObject.initialize

        """

        NormalSpoke.initialize(self)
        self._entry = self.builder.get_object("username")
        self._password = self.builder.get_object("password")
        self._domain = self.builder.get_object("domain")

    def refresh(self):
        """
        The refresh method that is called every time the spoke is displayed.
        It should update the UI elements according to the contents of
        self.data.

        :see: pyanaconda.ui.common.UIObject.refresh

        """

        self._entry.set_text(self.data.addons.org_amahi_setup.username)
        self._password.set_text(self.data.addons.org_amahi_setup.password)
        self._domain.set_text(self.data.addons.org_amahi_setup.domain)
        self._password.set_visibility(False) 
 
    def apply(self):
        """
        The apply method that is called when the spoke is left. It should
        update the contents of self.data with values set in the GUI elements.

        """        
        if not check_user_input(self._entry.get_text(),self._password.get_text(),self._domain.get_text()):
                             return 
        if not (check_credentials(self._entry.get_text(), self._password.get_text())):
                                                  return
            
        username = self._entry.get_text()
        password = self._password.get_text()
        domain = self._domain.get_text()

        ip_parts= ip_splitter()
        gateway = ip_parts[3].decode("utf-8")
        ip_address_parts = ip_getter(ip_parts)
    
        apikey = apikey_getter(username, password,domain, ip_address_parts)
        
        if not len(apikey):
                           return
        
        create_system_configuration_amahi(username, domain, ip_address_parts,apikey, gateway)
        #try:
         #                    check_output('wget -q --spider -U "Amahi-11-Express-x86_64" "https://api.amahi.org/api2/verify/'+self._entry.get_text()+'"', shell=True)
        #except CalledProcessError:
        #                     self.data.addons.org_amahi_setup.complete = False
        #                     return
        
        self.data.addons.org_amahi_setup.complete = True
        self.data.addons.org_amahi_setup.username = self._entry.get_text()
        self.data.addons.org_amahi_setup.password = self._password.get_text()
        self.data.addons.org_amahi_setup.domain = self._domain.get_text()
        
    def execute(self):
        """
        The excecute method that is called when the spoke is left. It is
        supposed to do all changes to the runtime environment according to
        the values set in the GUI elements.

        """

        # nothing to do here
        pass

    @property
    def ready(self):
        """
        The ready property that tells whether the spoke is ready (can be visited)
        or not. The spoke is made (in)sensitive based on the returned value.

        :rtype: bool

        """

        # this spoke is always ready
        return True

    @property
    def completed(self):
        """
        The completed property that tells whether all mandatory items on the
        spoke are set, or not. The spoke will be marked on the hub as completed
        or uncompleted acording to the returned value.

        :rtype: bool

        """

        #if len(self.data.addons.org_amahi_setup.text) <= 5:
        #                                    return 0
      
        if  self.data.addons.org_amahi_setup.complete:
                   return 1
        
        return 0

    @property
    def mandatory(self):
        """
        The mandatory property that tells whether the spoke is mandatory to be
        completed to continue in the installation process.

        :rtype: bool

        """

        return True

    @property
    def status(self):
        """
        The status property that is a brief string describing the state of the
        spoke. It should describe whether all values are set and if possible
        also the values themselves. The returned value will appear on the hub
        below the spoke's title.

        :rtype: str

        """
        username = self.data.addons.org_amahi_setup.username
        password = self.data.addons.org_amahi_setup.password
        domain = self.data.addons.org_amahi_setup.domain
        #text = self.data.addons.org_amahi_setup.text

        # If --reverse was specified in the kickstart, reverse the text
        #if self.data.addons.org_amahi_setup.reverse:
        #                                 text = text[::-1]

        if (len(username) == 0) or (len(password) == 0) or (len(domain) == 0) :
                         return _("Fill proper Username, Password and Domain")
        
        if self.data.addons.org_amahi_setup.complete:
                                return _("Account Verified")
        else:        
              return _("Incorrect Username/Password or Domain not proper")

    ### handlers ###
    def on_entry_icon_clicked(self, entry, *args):
        """Handler for the textEntry's "icon-release" signal."""
        
        entry.set_text("")

    def on_main_button_clicked(self, *args):
        """Handler for the mainButton's "clicked" signal."""

        # every GUIObject gets ksdata in __init__
        dialog = HelloWorldDialog(self.data)

        # show dialog above the lightbox
        with self.main_window.enlightbox(dialog.window):
            dialog.run()


class HelloWorldDialog(GUIObject):
    """
    Class for the sample dialog.

    :see: pyanaconda.ui.common.UIObject
    :see: pyanaconda.ui.gui.GUIObject

    """

    builderObjects = ["sampleDialog"]
    mainWidgetName = "sampleDialog"
    uiFile = "amahi_setup.glade"

    def __init__(self, *args):
        GUIObject.__init__(self, *args)

    def initialize(self):
        GUIObject.initialize(self)

    def run(self):
        """
        Run dialog and destroy its window.

        :returns: respond id
        :rtype: int

        """

        ret = self.window.run()
        self.window.destroy()

        return ret

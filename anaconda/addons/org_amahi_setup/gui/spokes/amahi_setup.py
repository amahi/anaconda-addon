from org_amahi_setup.categories.amahi_setup import AmahiCategory
from subprocess import check_output
from subprocess import call
from ipaddress import IPv4Network
import socket, struct
from subprocess import CalledProcessError
import http.client as httplib
from pyanaconda.ui.gui import GUIObject
from pyanaconda.ui.gui.spokes import NormalSpoke
from pyanaconda.ui.common import FirstbootSpokeMixIn

# export only the spoke, no helper functions, classes or constants
__all__ = ["AmahiSpoke"]

# import gettext
# _ = lambda x: gettext.ldgettext("amahi-anaconda-plugin", x)

# will never be translated
_ = lambda x: x
N_ = lambda x: x

def have_internet():
    conn = httplib.HTTPConnection("www.google.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return True
    except:
        conn.close()
        return False

def check_user_input(username,password,domain,install_code):
        import re
        
        #if both INSTALL_CODE and ACCOUNT field typed
        if ((len(username) != 0) or (len(password) != 0) or (len(domain) != 0)) and (len(install_code) != 0) :
                                    return 1
        #if install code is typed                            
        if len(install_code) != 0 : 
                                   return 2
  
        #check domain name proper or not
        m = re.search('^((https?|ftp|smtp):\/\/)?(www.)?[a-z0-9]+\.[a-z]+(\/[a-zA-Z0-9#]+\/?)*$',domain) 
        #check if any field empty
        if len(username) == 0:
                                                      return 3
        if len(password) == 0:
                                                      return 3
        if (len(domain) == 0):
                                                      return 3
        
        #checking domain
        try:
             m.group(0)
        except AttributeError:
                              return 3
        return 0

def check_install_code(install_code):
                                   if len(install_code) <= 5: #if install code too small
                                                      return False
                                   try:
                                       check_output('wget -q --spider -U "Amahi-11-Express-x86_64" "https://api.amahi.org/api2/verify/' + install_code + '"', shell=True)
                                   except CalledProcessError:
                                       return False  #if install code wrong
                                   
                                   return True #if install code is verified

def get_default_gateway_linux():
    """Read the default gateway directly from /proc."""
    with open("/proc/net/route") as fh:
        for line in fh:
            fields = line.strip().split()
            if fields[1] != '00000000' or not int(fields[3], 16) & 2:
                continue

            return socket.inet_ntoa(struct.pack("<L", int(fields[2], 16)))

def ip_splitter():
                          if have_internet(): #checking internet
                                         ip = get_default_gateway_linux() #getting gateway
                          else: 
                                         return False
                          #splitting gateway address 
                          try:
                               parts = ip.split('.')
                               if (len(parts) == 4) and all(0 <= int(part) < 256 for part in parts):
                                                                         return parts
                          except ValueError:
                                           return False
                          except (AttributeError, TypeError):
                                           return False

def ip_getter(parts):
                         #pinging ip address received from gateway and returning new ipv4 address in 4 parts
                         network = IPv4Network(parts[0] + '.' + parts[1] + '.' + parts[2] + '.0/24')
                         reserved = {  f'{parts[0]}.{parts[1]}.{parts[2]}.1',  f'{parts[0]}.{parts[1]}.{parts[2]}.2' , f'{parts[0]}.{parts[1]}.{parts[2]}.3'} #these ip address will not be used
                         hosts_iterator = (host for host in network.hosts() if str(host) not in reserved) 
                         for host in hosts_iterator:
                                          response = call("ping -c 3 " + str(host), shell=True)
                                          if response != 0:
                                                         return str(host).split('.')

def apikey_getter(username, password, domain, ip_address):
                        #call amahi api to get api key
                        try:
                              apikey = check_output(f'wget -q --spider -U "Amahi-11-Express-x86_64" "https://api.amahi.org/api2/nic-install?{username}&{password}&{domain}&{ip_address}"', shell=True)
                              return apikey.decode("utf-8")
                        except CalledProcessError:
                              return ""

#changing variables in system_configuration_amahi file by replacing it with received values
def create_system_configuration_amahi(username, domain, ip_address, apikey, gateway):
            call("sed -i 's/#apikey/" + apikey + "/' /usr/share/anaconda/addons/org_amahi_setup/system_configuration_amahi", shell=True)
            call("sed -i 's/#nick/" + username + "/' /usr/share/anaconda/addons/org_amahi_setup/system_configuration_amahi", shell=True)
            call("sed -i 's/#domain/" + domain + "/' /usr/share/anaconda/addons/org_amahi_setup/system_configuration_amahi", shell=True)
            call("sed -i 's/#net_point/" + ip_address[0] + "." + ip_address[1] + "." + ip_address[2] + "/' /usr/share/anaconda/addons/org_amahi_setup/system_configuration_amahi", shell=True)
            call("sed -i 's/#self-address/" + ip_address[3] + "/' /usr/share/anaconda/addons/org_amahi_setup/system_configuration_amahi", shell=True)
            call("sed -i 's/#gateway/" + gateway + "/' /usr/share/anaconda/addons/org_amahi_setup/system_configuration_amahi", shell=True)

class AmahiSpoke(FirstbootSpokeMixIn, NormalSpoke):
    """
    Class for the Amahi spoke. This spoke will be in the Amahi
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
    builderObjects = ["AmahiSpokeWindow", "buttonImage"]

    # the name of the main window widget
    mainWidgetName = "AmahiSpokeWindow"

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
        self._install_code = self.builder.get_object("install_code")

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
        self._install_code.set_text(self.data.addons.org_amahi_setup.install_code)
        self._password.set_visibility(False) 
 
    def apply(self):
        """
        The apply method that is called when the spoke is left. It should
        update the contents of self.data with values set in the GUI elements.

        """        
        #setting this to False to start checking again
        self.data.addons.org_amahi_setup.complete = False
        
        #checking user_input using function above and getting return value
        user_input_return =  check_user_input(self._entry.get_text(),self._password.get_text(),self._domain.get_text(),self._install_code.get_text())
        
        #if both field typed
        if user_input_return == 1: 
                                 self.data.addons.org_amahi_setup.both_field_typed = True
                                 return
        #if both field is not typed  
        self.data.addons.org_amahi_setup.both_field_typed = False
        
        #if install_code typed
        if user_input_return == 2: 
                                 self.data.addons.org_amahi_setup.install_code_selected = True
        else:
                                 self.data.addons.org_amahi_setup.install_code_selected = False
                                
        #if install_code is typed
        if self.data.addons.org_amahi_setup.install_code_selected :
                                                                   if check_install_code(self._install_code.get_text()):
                                                                                                                   self.data.addons.org_amahi_setup.complete = True
                                                                                                                   self.data.addons.org_amahi_setup.install_code = self._install_code.get_text()
                                                                   else:
                                                                       return
    
        #if username/password/domain field is blank
        if user_input_return == 3:
                             return

        #if proper Account Info format typed. Not verified
        self.data.addons.org_amahi_setup.username = self._entry.get_text()
        self.data.addons.org_amahi_setup.password = self._password.get_text()
        self.data.addons.org_amahi_setup.domain = self._domain.get_text() 

        #copying user input to a variable
        username = self._entry.get_text()
        password = self._password.get_text()
        domain = self._domain.get_text()
        
        #if right ipv4 gateway found then saved in ip_parts in 4 parts else return 
        if ip_splitter():
                         ip_parts = ip_splitter()
        else:
                         self.data.addons.org_amahi_setup.gateway_status = False
                         return
        #if right ipv4 gateway found
        self.data.addons.org_amahi_setup.gateway_status = True
        #storing last part of gateway
        gateway = ip_parts[3]
        #getting one free ip address
        ip_address_parts = ip_getter(ip_parts)

        #getting apikey
        apikey = apikey_getter(username, password,domain, ip_address_parts)
        if not len(apikey):
                           return
        
        #replace variables in system_configuration_amahi file with received values
        create_system_configuration_amahi(username, domain, ip_address_parts,apikey, gateway)

        #if everything went well 
        self.data.addons.org_amahi_setup.complete = True
        
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
        install_code = self.data.addons.org_amahi_setup.install_code

        #if both field is typed
        if self.data.addons.org_amahi_setup.both_field_typed :
                          return _("Type Account Info or INSTALL CODE, not both")

        #if install code is selected then do INSTALL CODE work
        if self.data.addons.org_amahi_setup.install_code_selected :
                                                                   if len(install_code) <= 5:
                                                                                  return _("Proper Install code not set")
        
                                                                   if self.data.addons.org_amahi_setup.complete:
                                                                                  return _("Install Code Verified")
                                                                   else:        
                                                                                  return _("Proper Install code not set") 
            
        if (len(username) == 0) or (len(password) == 0) or (len(domain) == 0) :
                         return _("Fill proper Account Info or INSTALL CODE")

        if not self.data.addons.org_amahi_setup.gateway_status: #if no proper IPv4 gateway available
                                return _("IPv4 gateway not available")

        if self.data.addons.org_amahi_setup.complete:
                                return _("Account Verified")
        else:        
              return _("Incorrect Username/Password/Domain")

    ### handlers ###
    def on_entry_icon_clicked(self, entry, *args):
        """Handler for the textEntry's "icon-release" signal."""
        
        entry.set_text("")

    def on_main_button_clicked(self, *args):
        """Handler for the mainButton's "clicked" signal."""

        # every GUIObject gets ksdata in __init__
        dialog = AmahiDialog(self.data)

        # show dialog above the lightbox
        with self.main_window.enlightbox(dialog.window):
            dialog.run()


class AmahiDialog(GUIObject):
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

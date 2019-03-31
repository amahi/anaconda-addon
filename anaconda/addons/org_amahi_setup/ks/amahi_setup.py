import os.path

from pyanaconda.addons import AddonData
from pyanaconda.iutil import getSysroot
from subprocess import call
from pykickstart.options import KSOptionParser
from pykickstart.errors import KickstartParseError, formatErrorMsg

# export HelloWorldData class to prevent Anaconda's collect method from taking
# AddonData class instead of the HelloWorldData class
# :see: pyanaconda.kickstart.AnacondaKSHandler.__init__
__all__ = ["AmahiData"]

HELLO_FILE_PATH = "/root/hello_world_addon_output.txt"



class AmahiData(AddonData):
    """
    Class parsing and storing data for the Hello world addon.

    :see: pyanaconda.addons.AddonData

    """

    def __init__(self, name):
        """
        :param name: name of the addon
        :type name: str

        """

        AddonData.__init__(self, name)
        self.text = ""
        self.username=""
        self.password=""
        self.domain="" 
        self.complete = False
        self.reverse = False

    def __str__(self):
        """
        What should end up in the resulting kickstart file, i.e. the %addon
        section containing string representation of the stored data.

        """

        addon_str = "%%addon %s" % self.name

        if self.reverse:
            addon_str += " --reverse"

        addon_str += "\n%s\n%%end\n" % self.text
        return addon_str

    def handle_header(self, lineno, args):
        """
        The handle_header method is called to parse additional arguments in the
        %addon section line.

        args is a list of all the arguments following the addon ID. For
        example, for the line:

            %addon org_fedora_hello_world --reverse --arg2="example"

        handle_header will be called with args=['--reverse', '--arg2="example"']

        :param lineno: the current line number in the kickstart file
        :type lineno: int
        :param args: the list of arguments from the %addon line
        :type args: list
        """

        op = KSOptionParser()
        op.add_option("--reverse", action="store_true", default=False,
                dest="reverse", help="Reverse the display of the addon text")
        (opts, extra) = op.parse_args(args=args, lineno=lineno)

        # Reject any additional arguments.
        if extra:
            msg = "Unhandled arguments on %%addon line for %s" % self.name
            if lineno != None:
                raise KickstartParseError(formatErrorMsg(lineno, msg=msg))
            else:
                raise KickstartParseError(msg)

        # Store the result of the option parsing
        self.reverse = opts.reverse

    def handle_line(self, line):
        """
        The handle_line method that is called with every line from this addon's
        %addon section of the kickstart file.

        :param line: a single line from the %addon section
        :type line: str

        """

        # simple example, we just append lines to the text attribute
        if self.text is "":
            self.text = line.strip()
        else:
            self.text += " " + line.strip()

    def finalize(self):
        """
        The finalize method that is called when the end of the %addon section
        (i.e. the %end line) is processed. An addon should check if it has all
        required data. If not, it may handle the case quietly or it may raise
        the KickstartValueError exception.

        """

        # no actions needed in this addon
        pass

    def setup(self, storage, ksdata, instclass, payload):
        """
        The setup method that should make changes to the runtime environment
        according to the data stored in this object.

        :param storage: object storing storage-related information
                        (disks, partitioning, bootloader, etc.)
        :type storage: blivet.Blivet instance
        :param ksdata: data parsed from the kickstart file and set in the
                       installation process
        :type ksdata: pykickstart.base.BaseHandler instance
        :param instclass: distribution-specific information
        :type instclass: pyanaconda.installclass.BaseInstallClass
        :param payload: object managing packages and environment groups
                        for the installation
        :type payload: any class inherited from the pyanaconda.packaging.Payload
                       class
        """

        # no actions needed in this addon
        pass

    def execute(self, storage, ksdata, instclass, users, payload):
        """
        The execute method that should make changes to the installed system. It
        is called only once in the post-install setup phase.

        :see: setup
        :param users: information about created users
        :type users: pyanaconda.users.Users instance

        """
        
        normalpath = os.path.normpath(getSysroot())
        #adding amahi repo
        call("chroot "+ normalpath+" rpm -Uvh http://f27.amahi.org/noarch/hda-release-10.5.0-1.noarch.rpm " , shell=True)
        
        #copy issue for message on top
        call("cp -vf /usr/share/anaconda/addons/org_amahi_setup/issue /usr/share/anaconda/addons/org_amahi_setup/issue.net "+normalpath+"/usr/bin", shell=True)
 
        #adding INSTALL CODE at the end of hda-install
        #call("sed -i 's/hda-install/hda-install "+self.text.upper()+"/' /usr/share/anaconda/addons/org_amahi_setup/hda-install-script.sh", shell=True)
        #get script in place
        call("cp -v /usr/share/anaconda/addons/org_amahi_setup/hda-install-script.sh "+normalpath+"/usr/bin", shell=True)
 
        #copy amahi configuration to /etc
        call("cp -v /usr/share/anaconda/addons/org_amahi_setup/system_configuration_amahi "+normalpath+"/etc", shell=True)
        
        #for amahi server setup message
        call("cp -v /usr/share/anaconda/addons/org_amahi_setup/amahi_message "+normalpath+"/usr/bin", shell=True)
        call("cp -rv /usr/share/anaconda/addons/org_amahi_setup/getty@tty1.service.d/ "+normalpath+"/etc/systemd/system/", shell=True)

        
        #enable script service 
        call("cp -v /usr/share/anaconda/addons/org_amahi_setup/amahi_setup.service "+normalpath+"/etc/systemd/system/", shell=True)
        call("chroot "+ normalpath+" systemctl enable amahi_setup.service" ,shell=True)


        
        #old commands commented out :-
        #call("echo 'hda-install "+self.text.upper()+"' >> "+normalpath+"/usr/bin/hda-install-script.sh", shell=True)
        #call("echo 'rm -rf /etc/systemd/system/getty@tty1.service.d ' >> "+normalpath+"/usr/bin/hda-install-script.sh", shell=True)
        #call("echo 'dhclient && dnf -y swap fedora-release generic-release' >> "+normalpath+"/usr/bin/hda-install-script.sh", shell=True)
        #call("echo 'mv -f /usr/bin/issue /usr/bin/issue.net /etc' >> "+normalpath+"/usr/bin/hda-install-script.sh", shell=True)
        #call("echo 'systemctl disable amahi_setup.service && reboot ' >> "+normalpath+"/usr/bin/hda-install-script.sh", shell=True)
 
        
        #call("chroot "+ normalpath+" hda-install "+" "+self.text.upper(), shell=Tr
        #hello_file_path = os.path.normpath(getSysroot() + HELLO_FILE_PATH)
        #with open(hello_file_path, "w") as fobj:
        #     fobj.write("%s\n" % users)

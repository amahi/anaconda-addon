# anaconda-addon
Amahi Anaconda Add-on

Directory Structure :-

```
root_folder
├─ ks
│  └─ __init__.py
├─ gui
│  ├─ __init__.py
│  └─ spokes
│     └─ __init__.py
├─ tui
|  ├─ __init__.py
|  └─ spokes
└─ __init__.py
```

Reference - https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/7/html-single/anaconda_customization_guide/index


Steps to make iso (everything in su) :-

First execute ```dnf -y install genisoimage isomd5sum```. Now begin :-


1. Download https://dl.fedoraproject.org/pub/fedora/linux/releases/27/Workstation/x86_64/iso/Fedora-Workstation-netinst-x86_64-27-1.6.iso into your working directory.

2. ```mkdir /mnt/iso```

3. ```mount -t iso9660 -o loop path/to/image.iso /mnt/iso```

4. ```mkdir ISO``` 

5. ```cp -pRf /mnt/iso ISO/```

6. ```umount /mnt/iso```

7. ```mkdir -p product/usr/share/```

8. ```git clone https://github.com/amahi/anaconda-addon.git```

9. ```cp  anaconda-addon/isolinux.cfg ISO/iso/isolinux/ && cp anaconda-addon/grub.cfg ISO/iso/EFI/BOOT/```
   
   Note  - ```isolinux.cfg``` is for BIOS bootmenu and ```grub.cfg``` is for UEFI bootmenu. Both file contain the following lines beside every option:-
   
   a) ```inst.ks=hd:LABEL=Fedora-WS-dvd-x86_64-27:/ks.cfg``` (to execute the kickstart file saved in installation directory)
   
   b) ```inst.updates=hd:LABEL=Fedora-WS-dvd-x86_64-27:/amahi.img``` (to load amahi.img saved in installation directory, where anaconda addon is saved. We will tell you that how you can create this file later.)

10. ```cp -f anaconda-addon/ks.cfg ISO/iso/``` #change $releasever in ```url --mirrorlist=http://mirrors.fedoraproject.org/mirrorlist?repo=fedora-$releasever&arch=$basearch``` to version number of Fedora installing, in ```ks.cfg``` file

11. ```chmod +x anaconda-addon/anaconda/addons/org_amahi_setup/hda-install-script.sh && chmod +x anaconda-addon/anaconda/addons/org_amahi_setup/amahi_message && cp -r anaconda-addon/anaconda anaconda-addon/icons product/usr/share/ && cp -r  anaconda-addon/lib64 product/usr```

12. ```cd product/ && find . | cpio -c -o | gzip -9cv > ../amahi.img``` #this will create amahi.img file where addon is saved

13. ```mv -f ../amahi.img ../ISO/iso```

14. ```cd ../ISO/iso```

15. ```genisoimage -U -r -v -T -J -joliet-long -V "Fedora-WS-dvd-x86_64-27" -volset "Fedora-WS-dvd-x86_64-27" -A "Fedora-WS-dvd-x86_64-27" -b isolinux/isolinux.bin -c isolinux/boot.cat -no-emul-boot -boot-load-size 4 -boot-info-table -eltorito-alt-boot -e images/efiboot.img -no-emul-boot -o ../'Amahi Express Install Disc 11.iso' . && implantisomd5 ../'Amahi Express Install Disc 11.iso'``` #your iso will be in path/to/ISO folder. Now boot it and enjoy.

    
    Note - in ```org_amahi_setup/ks/amahi_setup.py``` :-
    
    Check ```execute(self, storage, ksdata, instclass, users, payload):``` function 
    
    from where all commands get executed after installion.

    ```lib64/python3.7/site-packages/pyanaconda/installclass.py``` is for setting ```Geolocation=True`` for changing language automatically.

Booting into ISO :-

1. Select your language.

2. On next screen, select your TimeZone, Keyboard.

3. Boot into the FEDORA initially for automatic server Setup. FEDORA will reboot automatically after Amahi Server gets setup.

4. Have a cup of coffee. :)

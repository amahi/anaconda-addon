#!/bin/bash

#This will keep executing the command untill the previous command exit status is 0
while true
do
       dnf -y install hda-ctl
       if [ $? != 0 ]; then
                   killall dhclient && dhclient
                   continue
       fi
       break
done
sleep 10

#This will keep executing the command untill the previous command exit status is 0
while true
do
       hda-install 
       if [ $? != 0 ]; then
                   killall dhclient && dhclient
                   continue
       fi
       break
done

#to remove that 'Amahi server setup' message during startup
rm -rf /etc/systemd/system/getty@tty1.service.d

#This will keep executing the command untill the previous command exit status is 0
while true
do
       dhclient && dnf -y swap fedora-release generic-release
       if [ $? != 0 ]; then
                   killall dhclient && dhclient
                   continue
       fi
       break
done

#to copy the modified 'issue' for custom amahi message during Login prompt
mv -f /usr/bin/issue /usr/bin/issue.net /etc

#disabling amahi_setup so that amahi server setup script will not run
systemctl disable amahi_setup.service && reboot



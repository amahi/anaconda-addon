#!/bin/bash

while true

do
       dnf -y install freeglut-devel
       
       if [ $? != 0 ]; then
                   killall dhclient && dhclient
                   continue
       fi
       break

done

sleep 10

while true

do
       hda-install 

       
       if [ $? != 0 ]; then
                   killall dhclient && dhclient
                   continue
       fi
       break

done

rm -rf /etc/systemd/system/getty@tty1.service.d

while true

do
       dhclient && dnf -y swap fedora-release generic-release

       if [ $? != 0 ]; then
                   killall dhclient && dhclient
                   continue

       fi
       break

done


mv -f /usr/bin/issue /usr/bin/issue.net /etc

systemctl disable amahi_setup.service && reboot



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
'org_amahi_setup' will execute the following commands after installation :-
  
  rpm -Uvh http://f25.amahi.org/noarch/hda-release-10.0.0-1.noarch.rpm
  dnf -y install hda-ctl
  
  Tried and tested. 
  
  check "execute(self, storage, ksdata, instclass, users, payload)" function in "org_amahi_setup/ks/amahi_setup.py".
  
  ks.cfg file is to automate most of the installation task (except language, timezone, keyboard and user creation).

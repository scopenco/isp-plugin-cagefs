isp-plugin-cagefs
=================

This is an alternative plugin for ISPmanager that allow to administrate CloudLinux CageFS.

Icons are taken from vendor plugin.

Difference from vendor plugin:
- written in python
- redesign with low memory usage 
- verbose logging
- corrected work of checkbox (enable/disable CageFS) in user.edit form

Dependancies:
- python >= 2.4
- python-psutl

Installation:
- copy files from etc/ to /usr/local/ispmgr/etc/
- copy files from addon/ to /usr/local/ispmgr/addon/
- killall -9 ispmgr

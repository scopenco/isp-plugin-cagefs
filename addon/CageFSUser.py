#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Andrey Skopenko <andrey@scopenco.net>

PLUGIN_NAME = 'CageFSUser'

import sys
sys.path.insert(0, '/usr/local/ispmgr/addon')
from cli import ExitOk,Log,xml_doc,xml_error
from libcagefs import CageFS

from os import chdir
from sys import exit,stderr,stdin
from cgi import FieldStorage
from traceback import format_exc

try:
  import xml.etree.cElementTree as etree
except ImportError:
  try:
    import xml.etree.ElementTree as etree
  except ImportError:
    print('Failed to import ElementTree from any known place')

if __name__ == "__main__":
    chdir('/usr/local/ispmgr/')

    # activate logging
    # stderr ==> ispmgr.log
    log = Log(plugin=PLUGIN_NAME)
    stderr = log

    try:
        # get xml vars
        xmldoc = etree.parse(stdin).getroot()

        level = xmldoc.get('level')
        user = xmldoc.get('user')
        params = xmldoc.find('params')
        func = params.find('func').text
        if params.find('sok') != None:
            sok = params.find('sok').text
        else:
            sok = None

        log.write('user %s, level %s, func %s, sok %s' % (user, level, func, sok))

        if func != 'user':
            print xml_doc()
            raise ExitOk('no action')

        cagefs = CageFS(log)
        enabled_users = cagefs.get_users_enabled()

        # change elems
        for elem in xmldoc.findall('elem'):
            # create cagefs_status sub element
            cagefs_status = etree.SubElement(elem, 'cagefs_status')
            # check if user has cagefs enabled
            name = elem.find('name').text
            if name in enabled_users:
                cagefs_status.text = 'Enabled'
            else:
                cagefs_status.text = 'Disabled'

        print(etree.tostring(xmldoc, encoding="UTF-8"))
        raise ExitOk('done')

    except ExitOk, e:
        log.write(e)
    except:
        print xml_error('please contact support team', code_num='1')
        log.write(format_exc())
        exit(0)

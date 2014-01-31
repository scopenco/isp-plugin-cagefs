#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Andrey Skopenko <andrey@scopenco.net>

PLUGIN_NAME = 'CageFSUserEdit_a'

import sys
sys.path.insert(0, '/usr/local/ispmgr/addon')
from cli import ExitOk, Log, xml_doc, xml_error
from libcagefs import CageFS

from os import chdir
from sys import exit, stderr
from cgi import FieldStorage
from traceback import format_exc

if __name__ == "__main__":
    chdir('/usr/local/ispmgr/')

    # activate logging
    # stderr ==> ispmgr.log
    log = Log(plugin=PLUGIN_NAME)
    stderr = log

    try:
        # get cgi vars
        req = FieldStorage(keep_blank_values=True)
        func = req.getvalue('func')
        elid = req.getvalue('elid')
        sok = req.getvalue('sok')

        log.write('func %s, elid %s, sok %s' % (func, elid, sok))

        if func != 'user.edit':
            print xml_doc()
            raise ExitOk('no action')

        if not sok:
            print xml_doc()
            raise ExitOk('no action')

        #assert sok
        #assert func == 'user.edit'

        name = req.getvalue('name')
        if not name:
            raise Exception('name is not set')

        cagefs_mode = req.getvalue('cagefs_mode')
        if not cagefs_mode:
            raise Exception('cagefs_mode is not set')

        cagefs = CageFS(log)
        cagefs.set_user_mode(name, cagefs_mode)
        print xml_doc()
        raise ExitOk('done')

    except ExitOk, e:
        log.write(e)
    except:
        print xml_error('please contact support team', code_num='1')
        log.write(format_exc())
        exit(0)

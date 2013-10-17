#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Andrey Skopenko <andrey@scopenco.net>

PLUGIN_NAME = 'CageFSBackup'

import sys
sys.path.insert(0, '/usr/local/ispmgr/addon')
from cli import ExitOk,Log,xml_doc,xml_error
from libcagefs import CageFS

from os import chdir
from sys import exit,stderr
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

        if func != 'backupplan' and sok:
            print xml_doc()
            raise ExitOk('no action')

        #assert not sok
        #assert func == 'backupplan'

        cagefs = CageFS(log)
        cagefs.run_cagefsctl('--hook-install')
        print xml_doc()
        raise ExitOk('done')

    except ExitOk, e:
        log.write(e)
    except:
        print xml_error('please contact support team', code_num='1')
        log.write(format_exc())
        exit(0)

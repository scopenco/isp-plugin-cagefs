#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Andrey Skopenko <andrey@scopenco.net>

PLUGIN_NAME = 'CageFS'

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

        if func not in ['cagefs.main', 'cagefs.toggle', 'cagefs.status',
                        'cagefs.update_start', 'cagefs.update_progress',
                        'cagefs.update_done', 'cagefs.init_start',
                        'cagefs.init_progress', 'cagefs.init_done',
                        'cagefs.enable-all', 'cagefs.disable-all']:
            print xml_doc()
            raise ExitOk('no action')

        cagefs = CageFS(log)
        if func == 'cagefs.main':
            cagefs.cagefs_main()
        if func == 'cagefs.toggle':
            cagefs.cagefs_toggle()
        if func == 'cagefs.status':
            cagefs.cagefs_status()
        if func == 'cagefs.enable-all':
            cagefs.cagefsctl_run_cmd('--enable-all')
        if func == 'cagefs.disable-all':
            cagefs.cagefsctl_run_cmd('--disable-all')

        if func == 'cagefs.init_start':
            cagefs.cagefs_init_start()
        if func == 'cagefs.init_progress':
            cagefs.cagefs_init_progress()
        if func == 'cagefs.init_done':
            cagefs.cagefs_init_done()

        if func == 'cagefs.update_start':
            cagefs.cagefs_update_start()
        if func == 'cagefs.update_progress':
            cagefs.cagefs_update_progress()
        if func == 'cagefs.update_done':
            cagefs.cagefs_update_done()

        print cagefs.get_output()
        raise ExitOk('done')

    except ExitOk, e:
        log.write(e)
    except:
        print xml_error('please contact support team', code_num='1')
        log.write(format_exc())
        exit(0)

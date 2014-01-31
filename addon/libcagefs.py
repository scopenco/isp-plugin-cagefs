#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: Andrey Skopenko <andrey@scopenco.net>

'''
This module is a set of functions and classes
for CageFS administration in ISPmanager.
'''

# configs
CAGEFS_SKELETON = '/usr/share/cagefs-skeleton/bin'
CAGEFS_UPLOG = '/var/log/cagefs-update.log'

from xml.dom import minidom
from psutil import process_iter, NoSuchProcess, Process
from os.path import isdir, isfile
import subprocess as sp


class CageFS(object):
    '''this class desc all need funcs for cagefs view'''

    def __init__(self, log):
        # construct xml </doc>
        self.xml_root = minidom.Document()
        self.xml_doc = self.xml_root.createElement('doc')
        self.xml_root.appendChild(self.xml_doc)
        # logging
        self.log = log

    def __check_cagefsctl_run(self):
        '''check if proc cagefsctl already running'''

        # get process iterator
        procs = process_iter()
        try:
            for proc in procs:
                if proc.name == 'cagefsctl':
                    p = Process(proc.pid)
                    if ['--init', '--reinit'] in p.cmdline:
                        return 'init'
                    if '--update' in p.cmdline:
                        return 'update'
        except NoSuchProcess, e:
            pass

    def __cagefs_user_mode(self, change=False):
        '''get current cagefs user mode'''

        cagefs_state = self.run_cagefsctl('--display-user-mode')
        if 'CageFS is disabled.' in cagefs_state.split('\n'):
            if change:
                self.run_cagefsctl('--enable-cagefs')
            return 'CageFS is disabled'
        else:
            if change:
                self.run_cagefsctl('--disable-cagefs')
            if 'Mode: Enable All' in cagefs_state.split('\n'):
                return 'New users will be in CageFS'
            else:
                return 'New users will <b>not</b> be in CageFS'

    def run_cagefsctl(self, cmd):
        '''run cagefsctl command with args'''

        run_cmd = '/usr/sbin/cagefsctl %s' % cmd
        p = sp.Popen(run_cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
        self.log.write('command (%s) return %s' % (run_cmd, p.wait()))
        out = p.stdout.read()
        if not out:
            out = p.stderr.read()
        return out

    def set_user_mode(self, user, mode):
        '''enable/disable user'''

        if mode == 'on':
            cmode = 'enable'
        else:
            cmode = 'disable'

        cmd = '--%s %s' % (cmode, user)
        self.run_cagefsctl(cmd)
        cmd = '--set-default-user-status %s' % user
        self.run_cagefsctl(cmd)
        cmd = '--cpetc %s' % user
        self.run_cagefsctl(cmd)

    def check_user_mode_enabled(self):
        '''get current cagefs user mode output'''

        cagefs_state = self.run_cagefsctl('--display-user-mode')
        if 'CageFS is disabled.' not in cagefs_state.split('\n'):
            return 1

    def get_users_enabled(self):
        '''get list of enabled users'''

        cagefs_users = self.run_cagefsctl('--list-enabled')
        return [i for i in cagefs_users.split('\n') if 0 < len(i.split()) < 2]

    def get_users_disabled(self):
        '''get list of disabled users'''

        cagefs_users = self.run_cagefsctl('--list-disabled')
        return [i for i in cagefs_users.split('\n') if 0 < len(i.split()) < 2]

    def cagefs_init_start(self):
        '''start cagefs init'''

        # create output if cagefs already created
        if isdir(CAGEFS_SKELETON):
            self.xml_elem = self.xml_root.createElement('elem')
            self.xml_doc.appendChild(self.xml_elem)
            msg_t = '<message><![CDATA[<div style="margin-left:20px;' \
                    'margin-top:20px;">' \
                    'CageFS is already Initialized.' \
                    '</div>]]></message>'
            msg = minidom.parseString(msg_t).firstChild
            return self.xml_elem.appendChild(msg)

        # run init
        cagefsctl_state = self.__check_cagefsctl_run()
        if not cagefsctl_state:
            self.run_cagefsctl('--init --do-not-ask --silent &>/dev/null &')
            self.xml_redirect = self.xml_root.createElement('redirect')
            self.xml_doc.appendChild(self.xml_redirect)
            msg = self.xml_root.createTextNode(
                'location="ispmgr?func=cagefs.init_progress"')
            return self.xml_redirect.appendChild(msg)

    def cagefs_update_start(self):
        '''start cagefs update'''

        # create output if cagefs already created
        if not isdir(CAGEFS_SKELETON):
            self.xml_elem = self.xml_root.createElement('elem')
            self.xml_doc.appendChild(self.xml_elem)
            msg_t = '<message><![CDATA[<div style="margin-left:20px;' \
                'margin-top:20px;">' \
                'CageFS is not Initialized. ' \
                'Init CageFS to update CageFS Skeleton.' \
                '</div>]]></message>'
            msg = minidom.parseString(msg_t).firstChild
            return self.xml_elem.appendChild(msg)

        # run init
        cagefsctl_state = self.__check_cagefsctl_run()
        self.xml_redirect = self.xml_root.createElement('redirect')
        self.xml_doc.appendChild(self.xml_redirect)
        if not cagefsctl_state:
            self.run_cagefsctl('--update --do-not-ask --silent &>/dev/null &')
            msg = self.xml_root.createTextNode(
                'location="ispmgr?func=cagefs.init_progress"')
        else:
            msg = self.xml_root.createTextNode(
                'location="ispmgr?func=cagefs.update_progress"')
        return self.xml_redirect.appendChild(msg)

    def cagefs_init_progress(self):
        '''show cagefs init progress'''

        cagefsctl_state = self.__check_cagefsctl_run()
        if not cagefsctl_state:
            self.xml_redirect = self.xml_root.createElement('redirect')
            self.xml_doc.appendChild(self.xml_redirect)
            msg = self.xml_root.createTextNode(
                'location="ispmgr?func=cagefs.init_done"')
            return self.xml_redirect.appendChild(msg)

        self.xml_elem = self.xml_root.createElement('elem')
        self.xml_doc.appendChild(self.xml_elem)
        msg_t = '<message><![CDATA[<div style="margin-left:20px;' \
                'margin-top:20px;">Init Skeleton<br /><br />' \
                '<div id="UpdateProgress" style="width:80%; border: ' \
                '1px solid #000000; height:400px; overflow-y: auto;' \
                'font-size:14px;">...<br />'

        if isfile(CAGEFS_UPLOG):
           # tail last 100 lines
            run_cmd = '/usr/bin/tail -100 %r' % CAGEFS_UPLOG
            p = sp.Popen(run_cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
            self.log.write('command (%s) return %s' % (run_cmd, p.wait()))
            if p.stdout:
                out = p.stdout.read()
            else:
                out = p.stderr.read()

            for line in out.split('\n'):
                msg_t += '%r<br />' % line

        msg_t += '</div></div>]]></message>'
        msg = minidom.parseString(msg_t).firstChild
        return self.xml_elem.appendChild(msg)

    def cagefs_update_progress(self):
        '''show cagefs update progress'''

        # create output if cagefs already created
        if not isdir(CAGEFS_SKELETON):
            self.xml_elem = self.xml_root.createElement('elem')
            self.xml_doc.appendChild(self.xml_elem)
            msg_t = '<message><![CDATA[<div style="margin-left:20px;' \
                    'margin-top:20px;">CageFS is not Initialized. ' \
                    'Init CageFS to update CageFS Skeleton.' \
                    '</div>]]></message>'
            msg = minidom.parseString(msg_t).firstChild
            return self.xml_elem.appendChild(msg)

        cagefsctl_state = self.__check_cagefsctl_run()
        if not cagefsctl_state:
            self.xml_redirect = self.xml_root.createElement('redirect')
            self.xml_doc.appendChild(self.xml_redirect)
            msg = self.xml_root.createTextNode(
                'location="ispmgr?func=cagefs.update_done"')
            return self.xml_redirect.appendChild(msg)

        self.xml_elem = self.xml_root.createElement('elem')
        self.xml_doc.appendChild(self.xml_elem)
        msg_t = '<message><![CDATA[<div style="margin-left:20px;' \
                'margin-top:20px;">Updating Skeleton<br /><br />' \
                '<div id="UpdateProgress" style="width:80%; border:' \
                '1px solid #000000; height:400px; overflow-y: auto;' \
                'font-size:14px;">...<br />'
        if isfile(CAGEFS_UPLOG):
           # tail last 100 lines
            run_cmd = '/usr/bin/tail -100 %r' % CAGEFS_UPLOG
            p = sp.Popen(run_cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
            self.log.write('command (%s) return %s' % (run_cmd, p.wait()))
            if p.stdout:
                out = p.stdout.read()
            else:
                out = p.stderr.read()

            for line in out.split('\n'):
                msg_t += '%r<br />' % line

        msg_t += '</div></div>]]></message>'
        msg = minidom.parseString(msg_t).firstChild
        return self.xml_elem.appendChild(msg)

    def cagefs_init_done(self):
        '''show cagefs last log'''

        cagefsctl_state = self.__check_cagefsctl_run()
        if cagefsctl_state == 'init':
            self.xml_redirect = self.xml_root.createElement('redirect')
            self.xml_doc.appendChild(self.xml_redirect)
            msg = self.xml_root.createTextNode(
                'location="ispmgr?func=cagefs.init_progress"')
            return self.xml_redirect.appendChild(msg)

        self.xml_elem = self.xml_root.createElement('elem')
        self.xml_doc.appendChild(self.xml_elem)
        msg_t = '<message><![CDATA[<div style="margin-left:20px;' \
                'margin-top:20px; font-size:16px;">' \
                'CageFS was Initialized.<br /><br />' \
                '<div id="UpdateProgress" style="width:80%; ' \
                'border: 1px solid #000000; height:400px; ' \
                'overflow-y: auto; font-size:14px;">...<br />'
        if isfile(CAGEFS_UPLOG):
           # tail last 100 lines
            run_cmd = '/usr/bin/tail -100 %r' % CAGEFS_UPLOG
            p = sp.Popen(run_cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
            self.log.write('command (%s) return %s' % (run_cmd, p.wait()))
            if p.stdout:
                out = p.stdout.read()
            else:
                out = p.stderr.read()

            for line in out.split('\n'):
                msg_t += '%r<br />' % line

        msg_t += '</div></div>]]></message>'
        msg = minidom.parseString(msg_t).firstChild
        return self.xml_elem.appendChild(msg)

    def cagefs_update_done(self):
        '''show cagefs update last log'''

        # create output if cagefs already created
        if not isdir(CAGEFS_SKELETON):
            self.xml_elem = self.xml_root.createElement('elem')
            self.xml_doc.appendChild(self.xml_elem)
            msg_t = '<message><![CDATA[<div style="margin-left:20px;' \
                    'margin-top:20px;">' \
                    'CageFS is not Initialized.' \
                    'Init CageFS to update CageFS Skeleton.' \
                    '</div>]]></message>'
            msg = minidom.parseString(msg_t).firstChild
            return self.xml_elem.appendChild(msg)

        cagefsctl_state = self.__check_cagefsctl_run()
        if cagefsctl_state == 'update':
            self.xml_redirect = self.xml_root.createElement('redirect')
            self.xml_doc.appendChild(self.xml_redirect)
            msg = self.xml_root.createTextNode(
                'location="ispmgr?func=cagefs.update_progress"')
            return self.xml_redirect.appendChild(msg)

        self.xml_elem = self.xml_root.createElement('elem')
        self.xml_doc.appendChild(self.xml_elem)
        msg_t = '<message><![CDATA[<div style="margin-left:20px;' \
                'margin-top:20px; font-size:16px;">' \
                'Update Complete<br /><br />' \
                '<div id="UpdateProgress" style="width:80%; border:' \
                '1px solid #000000; height:400px; overflow-y: auto;' \
                'font-size:14px;">...<br />'
        if isfile(CAGEFS_UPLOG):
           # tail last 100 lines
            run_cmd = '/usr/bin/tail -100 %r' % CAGEFS_UPLOG
            p = sp.Popen(run_cmd, shell=True, stdout=sp.PIPE, stderr=sp.PIPE)
            self.log.write('command (%s) return %s' % (run_cmd, p.wait()))
            if p.stdout:
                out = p.stdout.read()
            else:
                out = p.stderr.read()

            for line in out.split('\n'):
                msg_t += '%r<br />' % line

        msg_t += '</div></div>]]></message>'
        msg = minidom.parseString(msg_t).firstChild
        return self.xml_elem.appendChild(msg)

    def cagefs_status(self):
        '''change cagefs status to enable/disable'''

        # create output if cagefs already created
        if not isdir(CAGEFS_SKELETON):
            self.xml_elem = self.xml_root.createElement('elem')
            self.xml_doc.appendChild(self.xml_elem)
            msg_t = '<message><![CDATA[<div style="margin-left:20px;' \
                    'margin-top:20px;">' \
                    'CageFS is not Initialized. ' \
                    'Init CageFS to update CageFS Skeleton.' \
                    '</div>]]></message>'
            msg = minidom.parseString(msg_t).firstChild
            return self.xml_elem.appendChild(msg)

        # create output for running cagefsctl
        cagefsctl_state = self.__check_cagefsctl_run()
        if cagefsctl_state in ['init', 'update']:
            self.xml_redirect = self.xml_root.createElement('redirect')
            self.xml_doc.appendChild(self.xml_redirect)
            if cagefsctl_state == 'init':
                msg = self.xml_root.createTextNode(
                    'location="ispmgr?func=cagefs.init_progress"')
            if cagefsctl_state == 'update':
                msg = self.xml_root.createTextNode(
                    'location="ispmgr?func=cagefs.update_progress"')
            return self.xml_redirect.appendChild(msg)

        self.__cagefs_user_mode(True)
        self.xml_redirect = self.xml_root.createElement('redirect')
        self.xml_doc.appendChild(self.xml_redirect)
        msg = self.xml_root.createTextNode(
            'location="ispmgr?func=cagefs.main"')
        return self.xml_redirect.appendChild(msg)

    def cagefs_toggle(self):
        '''run cagefs to toggle mode'''

        # create output for running cagefsctl
        cagefsctl_state = self.__check_cagefsctl_run()
        if cagefsctl_state in ['init', 'update']:
            self.xml_redirect = self.xml_root.createElement('redirect')
            self.xml_doc.appendChild(self.xml_redirect)
            if cagefsctl_state == 'init':
                msg = self.xml_root.createTextNode(
                    'ispmgr?func=cagefs.init_progress')
            if cagefsctl_state == 'update':
                msg = self.xml_root.createTextNode(
                    'ispmgr?func=cagefs.update_progress')
            return self.xml_redirect.appendChild(msg)

        if isdir(CAGEFS_SKELETON):
            self.run_cagefsctl('--toggle-mode')
            self.xml_redirect = self.xml_root.createElement('redirect')
            self.xml_doc.appendChild(self.xml_redirect)
            msg = self.xml_root.createTextNode(
                'location="ispmgr?func=cagefs.main"')
            return self.xml_redirect.appendChild(msg)
        else:
            self.xml_elem = self.xml_root.createElement('elem')
            self.xml_doc.appendChild(self.xml_elem)
            msg_t = '<message><![CDATA[<div style="margin-left:20px;' \
                    'margin-top:20px;">' \
                    'CageFS is not Initialized. ' \
                    'Init CageFS to toggle mode.' \
                    '</div>]]></message>'
            msg = minidom.parseString(msg_t).firstChild
            return self.xml_elem.appendChild(msg)

    def cagefs_main(self):
        '''show main cagefs page'''

        # create output for running cagefsctl
        cagefsctl_state = self.__check_cagefsctl_run()
        if cagefsctl_state in ['init', 'update']:
            self.xml_redirect = self.xml_root.createElement('redirect')
            self.xml_doc.appendChild(self.xml_redirect)
            if cagefsctl_state == 'init':
                msg = self.xml_root.createTextNode(
                    'ispmgr?func=cagefs.init_progress')
            if cagefsctl_state == 'update':
                msg = self.xml_root.createTextNode(
                    'ispmgr?func=cagefs.update_progress')
            return self.xml_redirect.appendChild(msg)

        # create output for current users list
        self.xml_elem = self.xml_root.createElement('elem')
        self.xml_doc.appendChild(self.xml_elem)
        msg_t = '<message><![CDATA[<table style="margin-left:20px;' \
                'margin-top:20px; width:98%;"><tr><td style="border:0px;">'
        if isdir(CAGEFS_SKELETON):
            msg_t += self.__cagefs_user_mode()
            msg_t += '</br></br>'
            users = self.get_users_enabled()
            if len(users) > 0:
                msg_t += '<b>Enabled Users</b> (%r)<br />' % len(users)
                msg_t += ';'.join(users)
                msg_t += '</br></br>'
            users = self.get_users_disabled()
            if len(users) > 0:
                msg_t += '<b>Disabled Users</b> (%r)<br />' % len(users)
                msg_t += ';'.join(users)
                msg_t += '</br></br>'
        else:
            msg_t += 'CageFS is not initialized!'
        msg_t += '</td></tr></table>]]></message>'
        msg = minidom.parseString(msg_t).firstChild
        return self.xml_elem.appendChild(msg)

    def cagefsctl_run_cmd(self, cmd):
        '''run cagefsctl command and redirect to main page'''

        # create output if cagefs already created
        if not isdir(CAGEFS_SKELETON):
            self.xml_euem = self.xml_root.createElement('elem')
            self.xml_doc.appendChild(self.xml_elem)
            msg_t = '<message><![CDATA[<div style="margin-left:20px;' \
                    'margin-top:20px;">' \
                    'CageFS is not Initialized. ' \
                    'Init CageFS to update CageFS Skeleton.' \
                    '</div>]]></message>'
            msg = minidom.parseString(msg_t).firstChild
            return self.xml_elem.appendChild(msg)

        # create output for running cagefsctl
        cagefsctl_state = self.__check_cagefsctl_run()
        if cagefsctl_state in ['init', 'update']:
            self.xml_redirect = self.xml_root.createElement('redirect')
            self.xml_doc.appendChild(self.xml_redirect)
            if cagefsctl_state == 'init':
                msg = self.xml_root.createTextNode(
                    'location="ispmgr?func=cagefs.init_progress"')
            if cagefsctl_state == 'update':
                msg = self.xml_root.createTextNode(
                    'location="ispmgr?func=cagefs.update_progress"')
            return self.xml_redirect.appendChild(msg)

        self.run_cagefsctl(cmd)
        self.xml_redirect = self.xml_root.createElement('redirect')
        self.xml_doc.appendChild(self.xml_redirect)
        msg = self.xml_root.createTextNode(
            'location="ispmgr?func=cagefs.main"')
        return self.xml_redirect.appendChild(msg)

    def get_output(self):
        '''return constructed xml output'''
        return self.xml_root.toxml('UTF-8')

if __name__ == "__main__":
    print __doc__

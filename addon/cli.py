#!/usr/bin/env python
# -*- coding: UTF-8 -*-
# Author: Andrey Skopenko <andrey@scopenco.net>
'''
This module is a set of funcs and classes for ispmanager plugin creation.
'''

# configs
LOG_FILE = '/usr/local/ispmgr/var/ispmgr.log'

from os import getpid
from xml.dom import minidom

class ExitOk(Exception):
    pass

# module 'logging' IMHO is not so convenient for this task
class Log(object):
    '''Class used for add debug to ispmgr.log'''
    def __init__(self, plugin=None, output=LOG_FILE):
        import time
        timenow = time.localtime(time.time())
        self.timef = time.strftime("%b %d %H:%M:%S", timenow)
        self.log = output;
        self.plugin_name = plugin;
        self.fsock = open(self.log, 'a+')
        self.pid = getpid()
        self.script_name = __file__

    def write(self,desc):
        if not (desc == "\n"):
            if (desc[-1:] == "\n"):
                self.fsock.write('%s [%s] ./%s \033[36;40mPLUGIN %s :: %s\033[0m' % \
                    (self.timef, self.pid, self.script_name, self.plugin_name, desc))
            else:
                self.fsock.write('%s [%s] ./%s \033[36;40mPLUGIN %s :: %s\033[0m\n' % \
                    (self.timef, self.pid, self.script_name, self.plugin_name, desc))

    def close(self):
        self.fsock.close()

def xml_doc(elem = None, text = None):
    '''base xml output <doc>...</doc>'''
    xmldoc = minidom.Document()
    doc = xmldoc.createElement('doc')
    xmldoc.appendChild(doc)
    if elem:
        emp = xmldoc.createElement(elem)
        doc.appendChild(emp)
        if text:
            msg_text = xmldoc.createTextNode(text)
            emp.appendChild(msg_text)
    return xmldoc.toxml('UTF-8')

def xml_error(text,code_num=None):
    '''base xml error output <doc><error>...</error></doc>'''
    xmldoc = minidom.Document()
    doc = xmldoc.createElement('doc')
    xmldoc.appendChild(doc)
    error = xmldoc.createElement('error')
    doc.appendChild(error)
    if code_num:
        code = xmldoc.createAttribute('code')
        error.setAttributeNode(code)
        error.setAttribute('code',str(code_num))
        if code_num in [2,3,6]:
            obj = xmldoc.createAttribute('obj')
            error.setAttributeNode(obj)
            error.setAttribute('obj',str(text))
            return xmldoc.toxml('UTF-8')
        elif code_num in [4,5]:
            val = xmldoc.createAttribute('val')
            error.setAttributeNode(val)
            error.setAttribute('val',str(text))
            return xmldoc.toxml('UTF-8')
    error_text = xmldoc.createTextNode(text.decode('utf-8'))
    error.appendChild(error_text)
    return xmldoc.toxml('UTF-8')

def domain_to_idna(dom):
    '''convert domain to idna format'''
    dom_u = unicode(dom, 'utf-8')
    return dom_u.encode("idna")

if __name__ == "__main__":
     print __doc__

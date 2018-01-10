#!/usr/bin/python
# -*- coding: utf-8 -*-

import sys

from entryclient import EntryClient



def enter(ip,containerID):

    appname = "test"
    access_token = "test"
    proc_name = "test"
    instance_no = "test"
    term_type = "xterm"
    endpoint = "ws://%s:8888/enter" % ip
    header_data = ["access-token: %s" % access_token,
                   "app-name: %s" % appname,
                   "proc-name: %s" % proc_name,
                   "instance-no: %s" % instance_no,
                   "term-type: %s" % term_type,
                   "containerID: %s" % containerID]
    try:
        client = EntryClient(endpoint, header=header_data)
        client.invoke_shell()
    except:
        print("Server stops the connection. Ask admin for help.")

def main():
    ip = sys.argv[1]
    contid = sys.argv[2]
    enter(ip,contid)

if __name__ == '__main__':
    main()
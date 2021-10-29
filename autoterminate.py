import argparse
import logging
import subprocess
import socket
import os,pwd
import datetime
import re
from email.mime.text import MIMEText
haserror = False

def main():
    """Runs 'p4 monitor show' to find long running processess. If a job exceeds X number of hours, it runs
    'p4 monitor kill' to mark it for termination."""
    p = argparse.ArgumentParser(description="Marks long running processes for termination.")
    p.add_argument('-p','--p4bin',dest='p4bin', default='/opt/icmanage/bin/p4',help='Filepath to P4 binary.')
    p.add_argument('-d', dest='daylim', default=14, help='Max number of hours a process can run before being marked for termination.',
                   type=int)
    p.add_argument('--servers', dest='svrlist', required=True,
                   help='CSV list of server hostnames. (--servers p4main:1666,p4rep:1777)')
    p.add_argument('-m', dest='emails', default="jeremy.yung@icmanage.com",
                   help='Email recipient list.(a@email.com,b@email.com)')
    p.add_argument('--debug', dest='debug', default=False, action='store_true', help='Turn on debug output.')
    args = p.parse_args()

    if args.debug:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

    print("a")
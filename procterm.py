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
    p.add_argument('--p4bin',dest='p4bin', default='/opt/icmanage/bin/p4',help='Filepath to P4 binary.')
    p.add_argument('-h', dest='hourlim', default=240, help='Max number of hours a process can run before being marked for termination.',
                   type=int)
    #p.add_argument('-p', dest='p4port', required=True, help='P4PORT for main server.')
    p.add_argument('-m', dest='emails', default="jeremy.yung@icmanage.com",
                   help='Email recipient list.(a@email.com,b@email.com)')
    p.add_argument('--debug', dest='debug', default=False, action='store_true', help='Turn on debug output.')
    args = p.parse_args()

    if args.debug:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    p4_cmd_prefix = "%s -p %s -u icmAdmin" % (args.p4bin,args.p4port)

    temp = "2282 I icmAdmin   115:05:54 IDLE"
    print(temp.split(' '))
    print(int((temp.split(' ')[5]).split(':')[0]))

def splitMon(line):
    splitline = line.split(' ')
    PID = splitline[0]
    status = splitline[1]
    hours = splitline[5].split(':')[0]
    return(PID,status,hours)

def runMonShow(p4prefix):
    cmdstr = "%s monitor show" % p4prefix
    return runCMD(cmdstr)

def runMonTerm(p4prefix,PID):
    cmdstr = "%s monitor terminate %s" % (p4prefix, PID)
    return runCMD(cmdstr)

def runCMD(cmdstr):
    logging.debug("Running \" %s \"" % cmdstr)
    process = subprocess.Popen(cmdstr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = process.communicate()
    stdout = result[0].decode("utf-8")
    stderr = result[1].decode("utf-8")
    return_code = process.returncode
    return (stdout,stderr,return_code)

if __name__ == '__main__':
    main()
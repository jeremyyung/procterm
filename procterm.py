import argparse
import logging
import subprocess
import re
from email.mime.text import MIMEText
import socket
import os,pwd
haserror = False

def main():
    """Runs 'p4 monitor show' to find long running processess. If a job exceeds X number of hours, it runs
    'p4 monitor kill' to mark it for termination."""
    p = argparse.ArgumentParser(description="Marks long running processes for termination.")
    p.add_argument('--p4bin',dest='p4bin', default='/opt/icmanage/bin/p4',help='Filepath to P4 binary.')
    p.add_argument('-l', dest='hourlim', default=240,
                   help='Max number of hours a process can run before being marked for termination.', type=int)
    p.add_argument('-p', dest='p4port', required=True, help='P4PORT for main server.')
    p.add_argument('-u', dest='p4user', required=False, default='icmAdmin', help='P4 super user.')
    p.add_argument('-m', dest='emails', default="jeremy.yung@icmanage.com",
                   help='Email recipient list.(a@email.com,b@email.com)')
    p.add_argument('--debug', dest='debug', default=False, action='store_true', help='Turn on debug output.')
    p.add_argument('--dryrun', dest='dryrun', default=False, action='store_true',
                   help='Do a dryrun without terminating processes.')
    args = p.parse_args()

    #splitMon(" 2282 I icmAdmin   95:04:52 IDLE ")
    if args.debug:
        logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)
    p4_cmd_prefix = "%s -p %s -u %s" % (args.p4bin,args.p4port,args.p4user)

    stdout,stderr,errorcode = runMonShow(p4_cmd_prefix)
    if errorcode > 0:
        errorstr = "P4 Error: \n %s" % stderr
        logging.error(errorstr)
        mailReport([errorstr],args.emails,args.hourlim)
    else:
        logging.debug(stdout)
        allprocs = stdout.split('\n')
        termlist = []
        for proc in allprocs:
            if proc != '':
                PID,hours,procstr = splitMon(proc)
                if hours > args.hourlim:
                    termlist.append(procstr)
                    if not args.dryrun:
                        logging.error("Terminating %s, runtime %s hours" % (PID,hours))
                        runMonTerm(p4_cmd_prefix, PID)
                    else:
                        logging.error("Dryrun: %s runtime is %s hours" % (PID, hours))
        if len(termlist) > 0 and not args.dryrun:
            mailReport(termlist,args.emails,args.hourlim)
    exit(0)

def splitMon(procstr):
    PID = re.search('^.?\d+',procstr).group().strip()
    #status = re.search(' \w ', line).group().strip()
    hours = int(re.search(' \d+(?=:)', procstr).group().strip())
    return(PID,hours,procstr)

def runMonShow(p4prefix):
    cmdstr = "%s monitor show -a" % p4prefix
    return runCMD(cmdstr)

def runMonTerm(p4prefix,PID):
    cmdstr = "%s monitor terminate %s" % (p4prefix, PID)
    return runCMD(cmdstr)

def runCMD(cmdstr):
    logging.debug("Running: %s" % cmdstr)
    process = subprocess.Popen(cmdstr, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    result = process.communicate()
    stdout = result[0].decode("utf-8")
    stderr = result[1].decode("utf-8")
    return_code = process.returncode
    return (stdout,stderr,return_code)

def mailReport(termlist, emails, hourlimit):
    logging.debug("Error(s) encountered, sending email notice to %s." % emails)
    report = '\n'.join(termlist)
    report += "\nNOTE: This email will be sent if an error was encountered as well.\n"
    report += "\nSent by\n"
    report += "Host:    %s\n" % socket.gethostname()
    report += "User:    %s\n" % pwd.getpwuid(os.getuid())[0]
    report += "Program: %s\n" % os.path.basename(__file__)
    logging.debug('Email message:\n' + report)

    msg = MIMEText(report)
    msg["To"] = emails
    msg["Subject"] = "Perforce processes running longer than %s hours" % hourlimit
    msg["From"] = "icmanage@xilinx.com"
    p = subprocess.Popen(["/usr/sbin/sendmail", "-t"], stdin=subprocess.PIPE)
    p.communicate(msg.as_bytes())

if __name__ == '__main__':
    main()
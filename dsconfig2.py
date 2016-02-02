#!/usr/bin/env python

# This script can change computer, host and local host names on a Mac,
# bind and unbind from Active Directory, enable mobile accounts,
# enable local homes, set AdminGroups for AD, and MORE.
#
# Help: ./DSconfig2.py --help
#
# E.g. ./DSconfig2.py -n MyNewComputerName -l -c -b -g SuperAdminGroup,TeacherGroups -s dc1
#
# Version 1.2 12/31/2015
#

import sys
import argparse
import os
import subprocess

ADuser = 'domainadmin'
Domain = 'isb.local'
OU = 'OU=Computers,OU=ISB,DC=isb,DC=local'
default_groups = 'SuperAdmin'

#Exit right away if root.
if os.getuid() != 0:
    print 'Script must be run as root.'
    sys.exit(1)

def changeComputerNames(computer_name):
    '''This changes the computer name, local hostname and the hostname.'''
    names = {
        'ComputerName' : computerName,
        'LocalHostName' : computerName,
        'hostname' : (computerName + '.' + Domain).lower()
    }
    for name in names:
        cmd = ['scutil', '--set', name, names[name] ]
        proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                                stderr=subprocess.PIPE)
        (out, err) = proc.communicate()

def unbind_AD(password):
    '''Unbinds the computer from AD'''
    cmd = [ 'dsconfigad', '-remove', '-username', ADuser, '-force', '-password', password ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    if err:
        print 'Unbind failed.'
        print err

def bind_AD(computerName, password):
    '''Binds the computer to AD.'''
    cmd = [ "dsconfigad", "-add", Domain, "-username", ADuser, "-force", "-password", password, \
    "-computer", computerName, "-ou", OU, "y" ]
    proc = subprocess.Popen(cmd, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    if err:
        print 'Bind failed.'
        print err

#Add above options to bindOPtions and set all options at once.
def bindOptions_AD(options):
    '''Set various AD options'''
    proc = subprocess.Popen(options, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE)
    (out, err) = proc.communicate()
    if err:
        print 'Setting options failed.'
        print err

def main():

    parser = argparse.ArgumentParser(description='This script can change the computer name and/or bind to AD.')

    parser.add_argument('-n', help='New computer name', action='store',
                        dest='name', required=True)

    parser.add_argument('-t', '--test', help='Prints back the options you selected, but does not apply them.',
                        action='store_true', dest='test', required=False)

    parser.add_argument('-b', help='Bind the computer to AD', action='store_true',
                        dest='bind', required=False)

    parser.add_argument('-c', help='Change computer name', action='store_true',
                        dest='change_name', required=False)

    parser.add_argument('-l', help='Enable "Force Local Homes"', action='store_true',
                        dest='local_homes', required=False)

    parser.add_argument('-k', help='Disable "Force Local Homes"', action='store_true',
                        dest='network_homes', required=False)

    parser.add_argument('-m', help='Enable mobile accounts', action='store_true',
                        dest='mobile_accounts',required=False)

    parser.add_argument('-s', help='Specify servername for preferred DC. FQDN created for you.', action='store',
                        dest='server', required=False)

    parser.add_argument('-g', help='Set the groups which are allowed Admin rights. Mulitple groups should\
                        be seperated by a comma. E.g. "AdminGroup,TestGroup"',
                        action='store', dest='groups', required=False)

    parser.add_argument('-p', help='The password used for binding', action='store',
                        dest='password', required=True)

    args = parser.parse_args()

    #list of AD config options, cmd is first option
    options = ['dsconfigad']

    if args.groups:
        for item in ('-groups', args.groups):
            options.append(item)
    elif default_groups:
        for item in ('-groups', default_groups):
            options.append(item)

    if args.local_homes:
        for item in ('-localhome', 'enable'):
            options.append(item)

    if args.mobile_accounts:
        for item in ('-mobile', 'enable', '-mobileconfirm', 'disable'):
            options.append(item)

    if args.server:
        preferred_server = args.server + '.' + Domain
        for item in ('-preferred', preferred_server):
            options.append(item)

    if args.network_homes:
        for item in ('-localhome', 'enable'):
            options.append(item)

    #Print out the arguments entered by user without doing anything
    if args.test:
        print args
        for arg in vars(args):
            if getattr(args, arg):
                print arg + ':', getattr(args, arg)
        print 'Command being sent to set options:', options
        sys.exit(0)

    #Will change the computer names if -c specified
    if args.change_name:
        changeComputerNames(args.name)

    #Will bind and change options, if specified.
    if args.bind:
        unbind_AD(args.password)
        bind_AD(args.name, args.password)
        bindOptions_AD(options)

if __name__ == "__main__":
    main()

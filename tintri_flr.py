#!/usr/bin/python
# -*- coding: iso-8859-1  -*-

#===============================================================================
#  The MIT License (MIT)
#
#  Copyright (C) 2015 Schaefer & Tobies SuC GmbH. 
#
#  See LICENSE File
#===============================================================================

#===============================================================================
# Changeable Part
#===============================================================================

TINTRI_RECOVER_DIR = "/tintri_recover"
dbg_path = "/root/.tintri"

#===============================================================================
# END OF user changeable Part
#===============================================================================

#
# uws: 2016.02.08
# File Level Recovery Support for Tintri FLR Snapshot Feature
#
import getopt, os, sys, pickle
from os.path import join, basename, islink
from subprocess import Popen, PIPE
from time import strftime

Version = "1.0.1"

DISK_BY_PATH = "/dev/disk/by-path"
SCSI_SEARCH_PATH = "/sys/class/scsi_host"
MOUNT = "/bin/mount"
UMOUNT = "/bin/umount"
FDISK = "/sbin/fdisk -l"

first_fdisk_file = join(dbg_path, 'first_fdisk_info.pickle')

verbose = 0
dbg_fd = None

def get_disk_mnt_info():
    """
        Get partition infos for the actual visible disks
    """

    part_info = {}

    #
    # get the mount information for the disk partitions
    #
    proc = Popen(MOUNT,
        stdin = PIPE,
        stdout = PIPE,
        stderr = PIPE,
        shell = True)

    for l in proc.stdout:
        if verbose > 2:
            print "l: %s" % l.strip()
        parms = l.split()
        if parms[0].find('/dev/') == 0:
            part_info[basename(parms[0])] = {'mnt_path' : parms[2]}

    if not os.path.exists(DISK_BY_PATH):
        print "ERROR: couldn't find directory \'%s\'" % DISK_BY_PATH
        sys.exit(5)
    for part in os.listdir(DISK_BY_PATH):
        fname = join(DISK_BY_PATH, part)
        if islink(fname):
            dev = basename(os.readlink(fname))
            if dev in part_info.keys():
                part_info[dev]['disk_path'] = part 
        else:
            print "ERROR: disk_path isn't a symbolic link: \'%s\'" % fname
            sys.exit(6)
    if verbose > 1:
        print part_info
    return part_info

def get_fdisk_info(dbg_fd, old_info=None):
    """
        Get FDISK info for machine
    """

    fdisk_info = {}
    proc = Popen(FDISK,
        stdin = PIPE,
        stdout = PIPE,
        stderr = PIPE,
        shell = True)

    for l in proc.stdout:
        if verbose > 1:
            print "fdisk: %s" % l.strip()

        dbg_fd.write(l)

        if l.find('Disk') == 0 and '/dev' in l:
            # new Disk Information
            parms = l.split()
            disk = basename(parms[1].strip(':'))

            if old_info and disk in old_info:
                old_disk = True # Disk Info exists and should not be added
                                # into the "new" dict
                continue
            else:
                old_disk = False
            fdisk_info[disk] = { 'size' : "%s %s" % (
                                                parms[2], parms[3].strip(',')),
                                 'partitions' : [],
                               }
        elif l.find('/dev/') == 0:
            if old_disk:
                continue
            boot = False
            parms = l.split()
            if parms[1] == '*': # boot flag
                second_param = 2
                boot = True
            else:
                second_param = 1
            part_info = { 'name' : basename(parms[0]),
                          'boot' : boot,
                          'start': parms[second_param],
                          'end'  : parms[second_param+1],
                        }
            fdisk_info[disk]['partitions'].append(part_info)
        else:
            continue

    if verbose > 1:
        print """fdisk_info: 
    %s """ % fdisk_info

    return fdisk_info


def search_for_new_disks():
    """
        send scsi search command to find new disks
    """
    for d in os.listdir(SCSI_SEARCH_PATH):
        scan_file = join(SCSI_SEARCH_PATH, d, "scan")
        cmd = "echo \"- - -\" >%s" % scan_file
        print "search_for_new_disks: cmd : %s" % cmd
        os.system(cmd)

def init_env():
    """
        initialize dbg area in "root" dir
    """
    global dbg_fd

    first_fdisk = None
    mnt_info = None
    if not 'linux' in sys.platform.lower():
        print "ERROR: this script is only usable on a LINUX system"
        sys.exit(99)

    if not os.path.isdir(dbg_path):
        os.makedirs(dbg_path)

    dbg_file = join(dbg_path, 'flr.dbg')
    dbg_fd = open(dbg_file, 'w')
    dbg_fd.write("""
================================================================================
    Start of script: %s    Version. %s
    """ % (strftime("%x %X "), Version))

    if os.path.exists(first_fdisk_file):
        msg = "orig_fdisk info allready exists! I will use this \'old\' info"
        dbg_fd.write("%s\n" % msg)
        if verbose:
            print msg

        fd = open(first_fdisk_file, 'r')
        pic = pickle.Unpickler(fd)
        first_fdisk = pic.load()
        mnt_info = pic.load()
        fd.close()
        dbg_fd.write("""OLD fdisk info:
    %s 
    \n""" % first_fdisk)

    return first_fdisk, mnt_info


def write_first_fdisk(first_fdisk, mnt_info):
    """
        Write the First fdisk information into a python pickle file
    """
    fd = open(first_fdisk_file, 'w')
    pic = pickle.Pickler(fd)
    pic.dump(first_fdisk)
    pic.dump(mnt_info)
    fd.close()


def mount_snap_disks(first_disk, new_disk, mnt_info):
    """
        Mount the new found partitions on "recover" paths
    """
    global TINTRI_RECOVER_DIR
    # Plausi
    if not len(first_disk.keys()) == len(new_disk.keys()):
        print """ERROR: Number of disks before snapshot Recover is not equal the
    number of the newly found disks:
        Nr Pre disks    : %s 
        Nr of new Disks : %s
    """ % (len(first_disk.keys()), len(new_disk.keys()))
        sys.exit(8)

    for disk in first_disk:
        for part in first_disk[disk]['partitions']:
            for ndisk in new_disk:
                if first_disk[disk]['size'] == new_disk[ndisk]['size'] and\
                   len(first_disk[disk]['partitions']) == \
                                        len(new_disk[ndisk]['partitions']):
                    # OK Size and nr. of partitions is equal search the
                    # correct partition and mount it
                    for npart in new_disk[ndisk]['partitions']:
                        if part['boot'] == npart['boot'] and \
                           part['start'] == npart['start'] and \
                           part['end'] == npart['end']:
                            if part['name'] not in mnt_info:
                                # swap or other not mounted partition
                                continue
                            mnt_name = mnt_info[part['name']]['mnt_path']
                            if mnt_name == '/':
                                mnt_name = 'SLASH'
                            mnt_dir = join(TINTRI_RECOVER_DIR,
                                                        basename(mnt_name))
                            cmd = "%s /dev/%s %s" % (MOUNT, npart['name'],
                                                                       mnt_dir)
                            if verbose:
                                print cmd
                            if not os.path.isdir(mnt_dir):
                                os.makedirs(mnt_dir)
                            os.system(cmd)

def reset(reset_all=False):
    """
        unmount the FLR Partitions
        reset_all : the pickle info will be removed too
    """
    for fname in os.listdir(TINTRI_RECOVER_DIR):
        mnt_dir = join(TINTRI_RECOVER_DIR, fname)
        if os.path.ismount(mnt_dir):
            cmd = "%s -l %s" % (UMOUNT, mnt_dir)
            if verbose:
                print cmd
            os.system(cmd)
        if reset_all:
            os.unlink(mnt_dir)

    if reset_all:
        if os.path.exists(first_fdisk_file):
            os.unlink(first_fdisk_file)
        if os.path.exists(TINTRI_RECOVER_DIR):
            os.unlink(TINTRI_RECOVER_DIR)

def usage():
    print """
USAGE: %s [-v]* [--reset | --reset_all] [--version]

    the meaning of the options:

        -v               add verbosity
        --reset          Unmount the FLR Partitions
        --reset_all      Unmount the FLR Partitions and remove all cached
                         informations about the Linux-partitions
        --version        print programm version and exit

    """ % basename(sys.argv[0])
    sys.exit(1)

if __name__ == '__main__':
    #
    # Start of the Main-Prog
    #
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'v',
                                            ['reset', 'reset_all','version'])
    except:
        usage()

    for o, a in opts:
        if o == "-v":
            verbose += 1
        elif o == '--reset':
            reset()
            sys.exit(0)
        elif o == '--reset_all':
            reset(True)
            sys.exit(0)
        elif o == '--version':
            print "%s : %s" % (basename(sys.argv[0]), Version)
            sys.exit(0)


    first_fdisk, mnt_info = init_env()
    if not first_fdisk:
        mnt_info = get_disk_mnt_info()
        first_fdisk = get_fdisk_info(dbg_fd)
        write_first_fdisk(first_fdisk, mnt_info)

    search_for_new_disks()
    new_fdisk = get_fdisk_info(dbg_fd, first_fdisk)

    if not new_fdisk:
        print "ERROR: no new Disks found: :-("
        sys.exit(0)

    mount_snap_disks(first_fdisk, new_fdisk, mnt_info)

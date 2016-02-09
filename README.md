# Tintri_LINUX_FLR
automatic mounting of Tintri-Storage-Snapshots for LINUX File-Level-Recovery (FLR)

================================================================================
                README: for the Python script tintri_flr.py
                uws: 2016.02.08
================================================================================

This python script "tintri_flr.py" intends to mount the existent
Tintri-Storage-Snapshots on the actual LINUX-System.

After you cloned a Tintri-Snapshot you need to mount the new SCSI-Devices
on your LINUX System. 
The only thing you have to do for this is call the script without any
option!
You must be "root" or use "sudo" to get the script working!

This script does the following:
    - determine the actual filesystem infomation.
    - search for new Snapshot-Disks in the SCSI environment.
    - generate new Mount-Points for the snapshot disks
    - mount the disks

================================================================================
##                Limitations
================================================================================
This script only works for "normal" partitions.
Volumemanager partitions couldn't be mounted from a tintri snapshot!

================================================================================
##                Environment
================================================================================
The filesystem information is stored in a information directory in the
home directory of the "root" user. This can be changed on top of the script
in the setting of the variable "dbg_path".

The mount-points are generated in a directory named "/tintri_recover".
This can also be changed in the top area of the script.

    #===========================================================================
    # Changeable Part
    #===========================================================================

    TINTRI_RECOVER_DIR = "/tintri_recover"
    dbg_path = "/root/.tintri"

    #===========================================================================
    # END OF user changeable Part
    #===========================================================================


================================================================================
##                Unmount
================================================================================
An unmount of the snapshot disks could be done by calling the script with the
option "--reset".


================================================================================
##                Resetting all informations
================================================================================
the script stores the information it had found a the first call in the
"dbg_path" (/root/.tintri). Normally it will work with the primary found
disk informations in furthermore calls. In normal cases this is very helpfull.
But sometimes (i.e. if the virtual machine has got a new real disk) you want
to start from scratch. If you need this you should call the "--reset_all"
option.

================================================================================
##                Examples
================================================================================
Given: a Ubuntu LINUX system with 3 Partitions "/", "/tmp" and "/home"
A Snapshot is restored with the Tintri WWW-GUI.

![mount VMrecover/file 01](/images/FLR_01.png)
Format: ![Alt Text](url)

![mount VMrecover/file 02](/images/FLR_02.png)
Format: ![Alt Text](url)

After completed restore you can start the "tintri_flr.py" and the
Snapshot-partitions will be mounted in the __TINTRI_RECOVER_DIR__.

    # ./tintri_flr.py -v
    orig_fdisk info allready exists! I will use this 'old' info
    search_for_new_disks: cmd : echo "- - -" >/sys/class/scsi_host/host0/scan
    search_for_new_disks: cmd : echo "- - -" >/sys/class/scsi_host/host1/scan
    search_for_new_disks: cmd : echo "- - -" >/sys/class/scsi_host/host2/scan
    /bin/mount /dev/sdd2 /tintri_recover/tmp
    /bin/mount /dev/sdd3 /tintri_recover/SLASH
    /bin/mount /dev/sdc1 /tintri_recover/home

================================================================================
##                Debugging
================================================================================
The script generates a debug file called __flr.dbg__ in the __dbg_path__
(*/root/.tintri*)  Here you can find all information about the primary disks
and the hopefully mounted snapshot disks. This file will be overwritten at
each run.

###             Debug File /root/.tintri/flr.dbg of the example above
# cat ~/.tintri/flr.dbg 

================================================================================
    Start of script: 02/09/16 16:57:39     Version. 1.0.1
    orig_fdisk info allready exists! I will use this 'old' info
    OLD fdisk info:
    {   'sda': {   'partitions': [   {   'boot': False,
                                         'end': '7999487',
                                         'name': 'sda1',
                                         'start': '2048'},
                                     {   'boot': False,
                                         'end': '15998975',
                                         'name': 'sda2',
                                         'start': '7999488'},
                                     {   'boot': True,
                                         'end': '41940991',
                                         'name': 'sda3',
                                         'start': '15998976'}],
                   'size': '21.5 GB'},
        'sdb': {   'partitions': [   {   'boot': False,
                                         'end': '83884031',
                                         'name': 'sdb1',
                                         'start': '2048'}],
                   'size': '42.9 GB'}}

    Disk /dev/sda: 21.5 GB, 21474836480 bytes
    64 heads, 32 sectors/track, 20480 cylinders, total 41943040 sectors
    Units = sectors of 1 * 512 = 512 bytes
    Sector size (logical/physical): 512 bytes / 512 bytes
    I/O size (minimum/optimal): 512 bytes / 512 bytes
    Disk identifier: 0x000bff36

       Device Boot      Start         End      Blocks   Id  System
    /dev/sda1            2048     7999487     3998720   82  Linux swap / Solaris
    /dev/sda2         7999488    15998975     3999744   83  Linux
    /dev/sda3   *    15998976    41940991    12971008   83  Linux

    Disk /dev/sdb: 42.9 GB, 42949672960 bytes
    255 heads, 63 sectors/track, 5221 cylinders, total 83886080 sectors
    Units = sectors of 1 * 512 = 512 bytes
    Sector size (logical/physical): 512 bytes / 512 bytes
    I/O size (minimum/optimal): 512 bytes / 512 bytes
    Disk identifier: 0x000e5f6a

       Device Boot      Start         End      Blocks   Id  System
    /dev/sdb1            2048    83884031    41940992   83  Linux

    Disk /dev/sdc: 42.9 GB, 42949672960 bytes
    255 heads, 63 sectors/track, 5221 cylinders, total 83886080 sectors
    Units = sectors of 1 * 512 = 512 bytes
    Sector size (logical/physical): 512 bytes / 512 bytes
    I/O size (minimum/optimal): 512 bytes / 512 bytes
    Disk identifier: 0x000e5f6a

       Device Boot      Start         End      Blocks   Id  System
    /dev/sdc1            2048    83884031    41940992   83  Linux

    Disk /dev/sdd: 21.5 GB, 21474836480 bytes
    64 heads, 32 sectors/track, 20480 cylinders, total 41943040 sectors
    Units = sectors of 1 * 512 = 512 bytes
    Sector size (logical/physical): 512 bytes / 512 bytes
    I/O size (minimum/optimal): 512 bytes / 512 bytes
    Disk identifier: 0x000bff36

       Device Boot      Start         End      Blocks   Id  System
    /dev/sdd1            2048     7999487     3998720   82  Linux swap / Solaris
    /dev/sdd2         7999488    15998975     3999744   83  Linux
    /dev/sdd3   *    15998976    41940991    12971008   83  Linux
    /bin/mount /dev/sdd2 /tintri_recover/tmp
    /bin/mount /dev/sdd3 /tintri_recover/SLASH
    /bin/mount /dev/sdc1 /tintri_recover/home

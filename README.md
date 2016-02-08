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
##                Debugging
================================================================================
the script generates a debug file called "flr.dbg" in the "dbg_path"
(/root/.tintri)  Here you can find all information about the primary disks
and the hopefully mounted sanpshot disks.


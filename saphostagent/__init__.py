from __future__ import absolute_import, print_function

# Import python libs
import logging
import os.path
import salt

# Import salt libs
import salt.utils.path
from salt.ext import six
from salt.exceptions import CommandExecutionError

# Set up logger
log = logging.getLogger(__name__)

# Define the module's virtual name
__virtualname__ = 'saphostagent'

def is_available():
    '''
    A function to check if systemd service sapinit exist!

    CLI Example::

        salt '*' saphostagent.is_available
    '''
    ret_sapinit = __salt__['service.available']('sapinit')
    log.info("ret_sapinit output: %s",ret_sapinit,exc_info=40)
    #print("ret_sapinit output: %s", ret_sapinit)
    if ret_sapinit is True:
        return ret_sapinit
    else:
        return (False, "saphostagent is maybe not installed. systemd service does not exist. Exit with error.")

def is_running():

    '''
    A function to check if systemd service sapinit is running!

    CLI Example::

        salt '*' saphostagent.is_running
    '''

    ret_avail = is_available()

    if ret_avail is True:
        ret_active = __salt__['service.status']('sapinit')
        log.info("ret_active output: %s",ret_active,exc_info=40)
        if ret_active is True:
            return True
        else:
            log.info("ret_avail output: %s",ret_avail,exc_info=1)
            return (False, "service sapinit is not running.")
    else:
        return (False, "service sapinit not found. Probably sap host agent is not installed.")



def get_version():

    '''
    A function finds sap host agent version and patch level!

    CLI Example::

        salt '*' saphostagent.get_version
    '''

    cmd = ['/usr/sap/hostctrl/exe/saphostexec', '-version']
    ret_run = is_running()
    final_result = {}
    log.info("debug ret_run: %s",ret_run,exc_info=1)
    if ret_run is True:
        subs = "kernel release"
        subs1 = "patch number"
        ret_get_vers = __salt__['cmd.run'](cmd).splitlines()
        res = [i for i in ret_get_vers if subs in i]
        get_vers = [int(a) for a in res[0].split() if a.isdigit()]

        res_patch_number = [x for x in ret_get_vers if subs1 in x]
        get_patch_number = [int(y) for y in res_patch_number[0].split() if y.isdigit()]
        final_result[subs] = get_vers[0]
        final_result[subs1] = get_patch_number[0]

        log.info(str(res[0]),exc_info=1)
        log.info(str(res_patch_number[0]),exc_info=1)
        return (True, final_result) 
    else:
        return (False, "saphostagent is not running or not installed. Exit.")

def extract_exe(**kwargs):

    '''
    A function extracts SAR file to a temp directory!

    CLI Example::

        salt '*' saphostagent.extract_exe SAPCAR="/mnt/software/SAPCAR" SAR_FILE="/nfsmnt/software/saphostagent45/SAPHOSTAGENT45_45-20009394.SAR" TARGET_DIR="/otherdir/for/extracted_files"
    '''

    target_dir = None
    sapcar = ""
    sarfile = ""
    log.info(kwargs,exc_info=1)

    for key, value in kwargs.items():
        if "SAPCAR" in key:
            sapcar = value

        if  "SAR_FILE" in key:
            sarfile = value
        
        if "TARGET_DIR" in key:
            target_dir = value

    if (len(sapcar) != 0) and (len(sarfile) != 0):

        ret_file_sapcar = __salt__['file.file_exists'](sapcar)
        ret_file_sarfile = __salt__['file.file_exists'](sarfile)

        if ret_file_sapcar is True:
            pass
        else:
            return (False, "sapcar not found!")
        
        if ret_file_sarfile is True:
            pass
        else:
            return (False, "sar file not found!")

        if target_dir is None:
            tmpdir = "/tmp/saphostagent"
            ret_file_dir = __salt__['file.dirname'](tmpdir)
        else:
            tmpdir = target_dir
            ret_file_dir = __salt__['file.dirname'](tmpdir)

        if ret_file_dir is True:
            pass
        else:
            ret_file_mkdir = __salt__['file.mkdir'](tmpdir)
            if ret_file_mkdir is True:
                pass
            else:
                return (False, "mkdir of TARGET_DIR failed.")

        cmd = [sapcar, "-xvf", sarfile, "-R", tmpdir]
        ret_extract = __salt__['cmd.run'](cmd)
        output = "SAR file extracted successfully to " + tmpdir
        output_dict = {}
        output_dict['SAPCAR extraction ouput'] = ret_extract
        output_dict['Summary'] = output
        if ret_extract is not None:
            return (True, output_dict)
    else:
        return (False, "no sufficient key value pairs provided. Refer to sys.doc saphostagent.extract_exe for more information.")


def upgrade(**kwargs):

    '''
    A function upgrades SAP Host Agent with given SAR file!

    CLI Example::

        salt '*' saphostagent.upgrades SAR_FILE="/nfsmnt/software/saphostagent45/SAPHOSTAGENT45_45-20009394.SAR"

    '''

    target_dir = None
    saphostexec = "/usr/sap/hostctrl/exe/saphostexec"
    sarfile = ""

    ret_saphostexec = __salt__['file.file_exists'](saphostexec)
    if ret_saphostexec is True:
        pass
    else:
        output_saphostexec = saphostexec + " not found."
        return (False, output_saphostexec)

    for key, value in kwargs.items():
        if  "SAR_FILE" in key:
            sarfile = value

    if (len(sarfile) != 0):
        ret_file_sarfile = __salt__['file.file_exists'](sarfile)

        if ret_file_sarfile is True:
            pass
            cmd = [saphostexec, "-upgrade", "-archive", sarfile]
        else:
            output_sarfile = sarfile + " not found."
            return (False, output_sarfile)
        ret_update = __salt__['cmd.run'](cmd)
        output = "SAP Host Agent upgraded successfully."
        output_dict = {}
        output_dict['Upgrade ouput'] = ret_update
        output_dict['Summary'] = output
        if ret_update is not None:
            return (True, output_dict)
    else:
        return (False, "no sufficient key value pairs provided. Refer to sys.doc saphostagent.upgrade for more information.")
# saphostagent
### This salt custom module helps to manage SAP HOST AGENT on minions.

```
# salt "hana-2*" sys.doc saphostagent 
saphostagent.extract_exe:

    A function extracts SAR file to a temp directory!

    CLI Example::

        salt '*' saphostagent.extract_exe SAPCAR="/mnt/software/SAPCAR" SAR_FILE="/nfsmnt/software/saphostagent45/SAPHOSTAGENT45_45-20009394.SAR" TARGET_DIR="/otherdir/for/extracted_files"
    

saphostagent.get_version:

    A function finds sap host agent version and patch level!

    CLI Example::

        salt '*' saphostagent.get_version
    

saphostagent.is_available:

    A function to check if systemd service sapinit exist!

    CLI Example::

        salt '*' saphostagent.is_available
    

saphostagent.is_running:

    A function to check if systemd service sapinit is running!

    CLI Example::

        salt '*' saphostagent.is_running
    

saphostagent.upgrade:

    A function upgrades SAP Host Agent with given SAR file!

    CLI Example::

        salt '*' saphostagent.upgrades SAR_FILE="/nfsmnt/software/saphostagent45/SAPHOSTAGENT45_45-20009394.SAR"
```
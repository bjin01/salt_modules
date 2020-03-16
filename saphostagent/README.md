# saphostagent
### This salt custom module helps to manage SAP HOST AGENT with following capabilities:
* __is_available__ - is saphostagent installed?
* __is_running__ - is saphostagent running as systemd service 'sapinit'?
* __get_version__ - returns SAP Host Agent Version and Patch Level.
* __extract_exe__ - extracts given SAR file.
* __upgrade__ - upgrades SAP Host Agent with given SAR file.

If you want to put the parameters in pillar sls named 'saphostagent.sls'
    Please create pillar data with below key names and structure. Key names must be exactly this you see below.
    Do not forget to add this pillar to your /srv/pillar/top.sls file.
```
    /srv/pillar/saphostagent.sls
    saphost:
      - sapcar_path: /nfsmnt/downloads
      - saphostagent_sar_file: SAPHOSTAGENT45_45-20009394.SAR
      - sar_file_path: /nfsmnt/downloads/saphostagent45
```

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

# saphostagent
### This salt custom module helps to manage SAP HOST AGENT with following capabilities:
* __is_available__ - is saphostagent installed?
* __is_running__ - is saphostagent running as systemd service 'sapinit'?
* __get_version__ - returns SAP Host Agent Version and Patch Level.
* __extract_sar__ - extracts given SAR file.
* __upgrade__ - upgrades SAP Host Agent with given SAR file.
* __get_pillar__ - shows pillar key value pairs for definition "saphost".

Using pillar to predefine the path and SAR file names create a pillar sls named 'saphostagent.sls'
Please create pillar data with below key names and structure. Key names must be exactly this you see below.

Do not forget __to add this pillar to your /srv/pillar/top.sls file.__

```
    /srv/pillar/saphostagent.sls
    saphost:
      - sapcar_path: </path/to/directory/where/SAPCAR-is-located>
      - saphostagent_sar_file: <SAR-full-file-name>
      - sar_file_path: </path/to/directory/where/SAR-file-is-located>
```
### Usage:

```
# salt "*" sys.doc saphostagent
saphostagent.extract_sar:

    A function extracts SAR file to a temp directory!

    If you want to put the parameters in pillar sls named 'saphostagent.sls'
    Please create pillar data with below key names and structure. Key names must be exactly this you see below.
    Do not forget to add this pillar to your /srv/pillar/top.sls file.

    /srv/pillar/saphostagent.sls
    saphost:
      - sapcar_path: </path/to/directory/where/SAPCAR-is-located>
      - saphostagent_sar_file: <SAR-full-file-name>
      - sar_file_path: </path/to/directory/where/SAR-file-is-located>

    if you don't use pillar you can also add the params as below:

    CLI Example::

        salt '*' saphostagent.extract_sar SAPCAR="/mnt/software/SAPCAR" SAR_FILE="/nfsmnt/software/saphostagent45/SAPHOSTAGENT45_45-20009394.SAR" TARGET_DIR="/otherdir/for/extracted_files"
    

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

    If you want to put the parameters in pillar sls named 'saphostagent.sls'
    Please create pillar data with below key names and structure. Key names must be exactly this you see below.
    Do not forget to add this pillar to your /srv/pillar/top.sls file.

    /srv/pillar/saphostagent.sls
    saphost:
      - sapcar_path: /nfsmnt/downloads
      - saphostagent_sar_file: SAPHOSTAGENT45_45-20009394.SAR
      - sar_file_path: /nfsmnt/downloads/saphostagent45

    if you don't use pillar you can also add the params as below:
    CLI Example::

        salt '*' saphostagent.upgrades SAR_FILE="/nfsmnt/software/saphostagent45/SAPHOSTAGENT45_45-20009394.SAR"

```

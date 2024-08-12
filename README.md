# Phase

Full and empty. Crescent and Gibbous. Wax and Wane. These are the different 
versions of the moon.

*But how should you version your files?*

If you're reading this, you are probably reading it on GitHub, a site 
dedicated to proper version control. However, sometimes you don't want 
proper version control. Sometimes you just want to slap a number on the damn 
filename and be done with it. This is where *phase* comes in. 


## Phase Options

```
# creates a config file & 'current' directory in the pwd
phase init
phase config [set OPTION | get OPTION] [PRODUCT_PATH]
# opens the latest version of the product managed by
# phase in the directory PRODUCT_PATH. Deletes older versions when doing
# so unless flag is used. PRODUCT_PATH is assumed to be pwd by default.
phase [--no-clean] [PRODUCT_PATH]
phase backup [--sample | --all]
```
Options are:
 - type: datetime | number
 - [backup]: shell commands to be used to backup the product to some 
   external services
    - backup.all.cmd: backup the entire directory
    - backup.current: backup the current version. Should accept a path 
      argument.
    - backup.sample.cmd: backup every Nth version, where N is set by the 
      frequency options
    - backup.regular.version_frequency
 - number.max: maximum no. of versions to be kept at any one time does 
   nothing if type == datetime
 - datetime.earliest: the earliest date to be kept at any one time.
 
 ---
 
 ## Dependencies
 
 - python >=3.6
    - due to 'import Pattern from typing'

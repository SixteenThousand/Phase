# Phase

Full and empty. Crescent and Gibbous. Wax and Wane. These are the different 
versions of the moon.

*But how should you version your files?*

If you're reading this, you are probably reading it on GitHub, a site 
dedicated to proper version control. However, sometimes you don't want 
proper version control. Sometimes you just want to slap a number on the damn 
filename and be done with it. This is where *phase* comes in. 


## Usage

Please note that phase is still only at v0.2; as such, most of these options 
do not work yet. See [development roadmap](#development-roadmap) for 
details.

```
phase [PRODUCT_PATH]
phase [-o|--only-open] [PRODUCT_PATH]
phase init [PRODUCT_PATH]
phase config [PRODUCT_PATH]
phase backup [--sample | --all | --release]
phase release
phase date [[-t|--time][=TIME_FORMAT]] FILE
phase desktop [--add|--remove] [PRODUCT_PATH]
```

### `phase [PRODUCT_PATH]`

Opens the 'product' at `PRODUCT_PATH`, or in the current working directory 
if no path is specified. This means that phase looks for a `.phase` file 
(see [Configuration](#configuration)) in the relevant directory and opens 
the file which matches the pattern given in that file with the highest 
version number.

Phase will also backup files with version numbers that are divisible by a 
number given in the config file, and delete older versions and older backup 
versions, again according to values given in the config file.

### `phase [-o|--only-open] [PRODUCT_PATH]`

Same as the previous option, but skip any deletion/backup operations.

### `phase init [PRODUCT_PATH]`

Creates a `.phase` file in the current working directory (or at 
`PRODUCT_PATH` if specified), so that some files in that directory are 
version controlled by phase.

Before making the file, phase prompts the user to enter values for various 
configuration options (see [Configuration](#configuration) below), which can 
be changed later by either editing the configuration file for that product, 
or by re-running `phase init` and responding 'no' when asked if they want to 
overwrite the existing configuration file.

Phase will also prompt the user to create a desktop entry file^1

### `phase config [PRODUCT_PATH]`

An alias for `phase init` (see above).

### `phase backup [--sample | --all | --release]`

Just make backups of the product.
- `--sample` does the same backing up as is done whern running phase with no 
  options
- `--all` runs a given shell command which should make a copy of the entire 
  directory somewhere (ideally to some remote source, possibly using 
  [rclone](rclone.org)).
- `--release` makes a copy of only the latest version, and adds a 
  date-time-stamp to the filename, the format of which can be specified in 
  the config file (see [Configuration](#configuration)).

### `phase release`

An alias for `phase backup --release`.

### `phase date [[-t|--time][=TIME_FORMAT]] FILE`

Adds a date-time-stamp to `FILE`, using the format `TIME_FORMAT`. 
`TIME_FORMAT` uses the following codes:
- `%y` => year
- `%m` => month
- `%d` => day (of month)
- `%H` => hour (using a 24-hour clock)
- `%M` => minute
- `%S` => second^2
Time & date information will use the system locale.
Note this is the only phase option that has nothing to do with a 
version-managed product.

### `phase desktop [--add|--remove] [PRODUCT_PATH]`

Adds or removes a desktop entry file^1 for the product at 
`PRODUCT_PATH`/current working directory.

---

## Getting Started

Phase is literally just a python script (specifically it is the `phase.py` 
you see above), so all you need to do to use it is get a copy of that file, 
remove the `.py` extension, and put it somewhere on your system's `PATH`.

See dependencies below for more specific information, but that should be it.

Go to the last tagged commit to get the latest (more-or-less) stable 
version.

### Dependencies

- python >=3.6 (this is due to the `Pattern` type from the `typing` module 
  being used)
- a UNIX-like operating system (i.e. not Windows)


## Configuration

Exactly *how* phase operates on a particular product is determined by a file 
named `.phase` in the product directory. An example of a `.phase` file is 
given below. Note that the file is in [toml](https://toml.io/en/) format.
```
# The pattern phase uses to identify product files; the %V represents where 
# the version number will go.
pattern = 'LS13_And-It-Goes-On_v%V.ods'

# The maximum number of versions phase should leave behind when cleaning up 
# old versions. So in this case, if versions 23-35 were present, then phase 
# would delete versions 23 & 24 so that only the latest 11 versions are
# left.
limit = 11



[backup]
# The configuration used when running phase backup --sample or in the backup 
# stage when running phase with no arguments.
[backup.sample]

# The frequency of backups; so in this case versions 5,10,15,... will get 
# backed up if present.
frequency = 5

# The place to put the backup files.
destination = "./Regular_Back-ups"

# The number of sample backups to leave when cleaning up; works similarly to 
# the other limit option.
limit = 10


# The configuration used when running phase backup --release or phase
# release.
[backup.release]

# The date-time format used when adding a date to the filename. See the 
# documentation for 'phase date' (under #Usage) for definitions of the %x 
# codes.
format = '%y%m%d-%H%M%S'

# The place to put the copy of the latest version.
destination = './Deep Storage'


[backup.all]
# The shell command run when using 'phase backup --all'.
cmd = 'rclone sync . GoogleDriveRemote:/directory/in/my/google/drive'
 ```
 
---
 
## Development Roadmap

- [x] phase [PRODUCT_PATH]
- [ ] phase [-o|--only-open] [PRODUCT_PATH]
- [ ] phase backup [--sample | --all | --release]
- [ ] phase release
- [ ] phase date [[-t|--time][=TIME_FORMAT]] FILE
- [ ] phase desktop [--add|--remove] [PRODUCT_PATH]
- [ ] phase init [PRODUCT_PATH]
- [ ] phase config [PRODUCT_PATH]

---

1. Desktop Entry Files<br/>
A *desktop entry file* is a file, used on linux systems, which allows 
various pieces of a software to know what applications are installed in the 
system, and how to open them. Having a desktop entry means that thing will 
appear on your start menu, and can be launched from a GUI app launcher. Very 
handy if you don't fancy opening a terminal every time you want to open a 
product managed by phase.

2. *Hopefully* you will never need this...

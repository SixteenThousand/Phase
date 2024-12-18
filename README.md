<h1 style="text-align: center; font-size: 75px;"> <img src="./Phase.svg" 
height="60" /> Phase </h1>

*Full and empty. Crescent and Gibbous. Wax and Wane. These are the different 
versions of the moon.*

But how should you version your files?

If you're reading this, you are probably reading it on GitHub, a site 
dedicated to proper version control. However, sometimes you don't want 
proper version control. Sometimes you just want to slap a number on the damn 
filename and be done with it. This is where *phase* comes in. 


## Usage

```
phase [PRODUCT_PATH]
phase [-o|--only-open] [PRODUCT_PATH]
phase init [PRODUCT_PATH]
phase backup [--sample | --all | --release] [PRODUCT_PATH]
phase release [PRODUCT_PATH]
phase date [[-f|--format] STAMP_FORMAT] [[-d|--output-directory] DIRECTORY] FILE
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

### `phase backup [--sample | --all | --release] [PRODUCT_PATH]`

Just make backups of the product.
- `--sample` does the same backing up as is done whern running phase with no 
  options
- `--all` runs a given shell command which should make a copy of the entire 
  directory somewhere (ideally to some remote source, possibly using 
  [rclone](rclone.org)).
- `--release` makes a copy of only the latest version, and adds a 
  date-time-stamp to the filename, the format of which can be specified in 
  the config file (see [Configuration](#configuration)).

### `phase release [PRODUCT_PATH]`

An alias for `phase backup --release`.

### `phase date [[-f|--format] STAMP_FORMAT] [[-d|--output-directory] DIRECTORY] FILE`

Creates a copy of `FILE` with a date-time-stamp added to the filename, using 
the format `STAMP_FORMAT` and in the directory `DIRECTORY`.

`STAMP_FORMAT` is parsed using the python `datetime.strftime` function (see
<https://docs.python.org/3/library/datetime.html#datetime.datetime#date.strftime>
for docs). The main ones you will likely want to use are:
- `%Y` => year
- `%m` => month
- `%d` => day (of month)
- `%H` => hour (using a 24-hour clock)
- `%M` => minute
- `%S` => second^2
Time & date information will use the system locale. The date-time-stamp will 
be added to the file name just before the file extension, if any.
Note this is the only phase option that has nothing to do with a 
version-managed product.
It defaults to `_%Y%m%d-%H%M%S`.

`DIRECTORY` defaults to the current directory.

### Examples

- `phase date -t='%Y-%m-%d' something.pdf` will rename 'something.pdf' to 
  'something_2024-08-29.pdf'
- `phase date -t='%m%d' something.otherthing.pdf` will rename 
  'something.otherthing.pdf' to 'something_0829.otherthing.pdf'

### `phase desktop [--add|--remove] [PRODUCT_PATH]`

Adds or removes a desktop entry file^1 for the product at 
`PRODUCT_PATH`/current working directory.

---

## Getting Started

Check you have the required dependencies, clone this repo to your machine, 
and run `make install` (obviously you will need GNU Make for this).

See dependencies below for more specific information, but that should be it.

Go to the last tagged commit to get the latest stable version.

### Dependencies

- python >=3.6 (this is due to the `Pattern` type from the `typing` module 
  being used)
- a UNIX-like/POSIX operating system (i.e. not Windows)
- ImageMagick (this is just to make the app icon; it can be circumvented, 
  but you'll need to change the build script slightly to do this, and it 
  will likely cause the app icon to not render properly)


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
format = '%Y%m%d-%H%M'

# The place to put the copy of the latest version.
destination = './Deep Storage'


[backup.all]
# The shell command run when using 'phase backup --all'.
cmd = 'rclone sync . GoogleDriveRemote:/directory/in/my/google/drive'
 ```
 
---
 
### Development Wishlist

These features may never be added, but are here for future reference should 
I find some spare time for them:
- [ ] Allow phase to put date-time-stamps anywhere in the file name, 
  possibly by changing how the STAMP_FORMAT variable works.
- [ ] Remove the need to not use single quotes in answers to initialisation 
  prompts; when making a desktop file, punctuation (specifically ') will 
  break the phase config, since you'll get a value like 'I'm tired', which 
  is invalid TOML
- [ ] make desktop entry files always use 'phase' as GenericName
- [ ] Add more to help, including documentation of python datetime format 
  codes; maybe make a `phase help command`?
- [ ] Allow release to use a filename with a different extension; maybe have 
  a backup.release.extension attribute?
- [ ] Allow date-time-stamps to be used as version numbers
- [ ] create a `phase info` command to query the .phase file

---

1. Desktop Entry Files<br/>
A *desktop entry file* is a file, used on linux systems, which allows 
various pieces of a software to know what applications are installed in the 
system, and how to open them. Having a desktop entry means that thing will 
appear on your start menu, and can be launched from a GUI app launcher. Very 
handy if you don't fancy opening a terminal every time you want to open a 
product managed by phase.

2. *Hopefully* you will never need this...

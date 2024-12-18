#!/bin/env python3

import enum
import os
import re
import shutil
import sys
import textwrap
import tomllib
from datetime import datetime
from typing import (
    Pattern,
    Match,
    List,
    Tuple,
    Any,
    TextIO
)


type Version = int
type Product = List[Tuple[str,Version]]

DESKTOP_FILES_LOC: str = \
    f"{os.getenv("HOME")}/.local/share/applications/phase"

# Represents main action for phase to take; default is to open the latest
# version & do clean-up
@enum.unique
class Action(enum.Enum):
    DEFAULT = "default"
    DATE = "date"
    BACKUP = "backup"
    RELEASE = "release"
    DESKTOP = "desktop"
    INIT = "init"

@enum.unique
class BackupAction(enum.Enum):
    ALL = "--all"
    RELEASE = "--release"
    SAMPLE = "--sample"

# Represents the options specified at the commandline by user, after being 
# parsed
class Flags():
    def __init__(self):
        self.action: Action = Action.DEFAULT
        self.help: bool = False
        self.version: bool = False
        self.only_open: bool = False
        self.product_path: str = os.getcwd()
        self.stamp_format: str = ""
        self.output_dir: str = os.getcwd()
        self.backup_action: BackupAction
        self.desktop_remove: bool



def check_is_product_dir(config: dict[str,Any],versions: Product):
    if not config:
        print(
            textwrap.dedent("""\
            \x1b[1;31mPhase Error: No .phase file found.
            \x1b[0mThe directory you have specified is not managed by phase.
            If you wish for files in this directory to be 
            managed by phase, please run
                \x1b[1mphase init\x1b[0m
            in this directory or
                \x1b[1mphase init path/to/this/directory\x1b[0m
            outside of it.
            """),
            file=sys.stderr
        )
        sys.exit(1)
    if not versions:
        print(
            textwrap.dedent("""\
                \x1b[1;31mPhase Error: No product files found.
                \x1b[0mThere are no product files in this directory yet.
                Please make at least 1 product file before using phase here.
            """),
            file=sys.stderr
        )
        sys.exit(1)

def main():
    flags = flagparse(sys.argv)
    flags.product_path = os.path.abspath(flags.product_path)
    if flags.action != Action.DATE:
        os.chdir(flags.product_path)
    if flags.version:
        print("Phase, v0.8.3 - The Best Worst Form Of Version Control")
        sys.exit(0)
    if flags.help:
        print(textwrap.dedent("""\
            Phase, v0.8.3 - The Best Worst Form Of Version Control
            
            Usage:
            \x1b[1mphase [PRODUCT_PATH]\x1b[0m
                Opens the latest version of the product at PRODUCT_PATH/the current working directory.
                Also deletes older versions and makes some backups
            \x1b[1mphase [-o|--only-open] [PRODUCT_PATH]\x1b[0m
                Same as above, but skips the backup and clean steps
            \x1b[1mphase init [PRODUCT_PATH]\x1b[0m
                Tell phase to manage files in PRODUCT_PATH/the current working directory
            \x1b[1mphase backup [--sample | --all | --release] [PRODUCT_PATH]\x1b[0m
                Make backup copies of some versions of the product.
                \x1b[1m--sample\x1b[0m Copies every Nth version, where N is 
                    a number you can configure (default 5)
                \x1b[1m--release\x1b[0m Copies the latest version, and 
                    appends a date-time stamp to the copy
                \x1b[1m--all\x1b[0m Runs a shell command, which you configure.
                    This command \x1b[3mshould\x1b[0m backup the whole directory,
                    but really it could do anything
            \x1b[1mphase release [PRODUCT_PATH]\x1b[0m
                Alias for phase backup --release
            \x1b[1mphase date [[-f|--format] STAMP_FORMAT] [[-d|--output-directory] DIRECTORY] FILE\x1b[0m
                Appends a date-time stamp to the name of FILE in format STAMP_FORMAT and puts the result
                in DIRECTORY.
                    STAMP_FORMAT defaults to yyyymmdd-HHMMSS
                    DIRECTORY defaults to the current directory
                This is the only command which does not require a phase-managed set of files (a "product")
            \x1b[1mphase desktop [--add|--remove] [PRODUCT_PATH]\x1b[0m
                Create or remove a desktop entry file for the product at PRODUCT_PATH/the current
                working directory.
                This option is only useful on Linux systems
        """))
        sys.exit(0)
    # load product configration
    config: dict[str,Any] = dict()
    versions: Product = []
    if os.path.exists("./.phase"):
        with open("./.phase","rb") as fp:
            config = tomllib.load(fp)
        config["regex"] = pat_to_regex(config["pattern"])
        versions = get_versions(config["regex"])
    match flags.action:
        case Action.DATE:
            new_name: str = date(
                flags.product_path,
                # a nice default format is provided
                flags.stamp_format or "_%Y%m%d-%H%M%S",
                dst=flags.output_dir
            )
            print(f"copy {flags.product_path} -> {new_name}")
        case Action.BACKUP:
            check_is_product_dir(config,versions)
            match flags.backup_action:
                case BackupAction.ALL:
                    cmd: str = config["backup"]["all"]["cmd"]
                    print(f"Running {cmd}")
                    os.system(cmd)
                    print("Done!")
                case BackupAction.SAMPLE:
                    backup_sample(
                        versions,
                        config["regex"],
                        config["backup"]["sample"]
                    )
                case BackupAction.RELEASE:
                    date(
                        versions[0][0],
                        flags.stamp_format or \
                            config["backup"]["release"]["format"],
                        dst=config["backup"]["release"]["destination"]
                    )
        case Action.DESKTOP:
            check_is_product_dir(config,versions)
            if flags.desktop_remove:
                remove_desktop_file(flags.product_path,config)
            else:
                add_desktop_file(flags.product_path,config)
        case Action.INIT:
            initialise(flags.product_path)
        case _:
            check_is_product_dir(config,versions)
            if not flags.only_open:
                # make backups
                backup_sample(
                    versions,
                    config["regex"],
                    config["backup"]["sample"],
                )
                # clean up old versions, both in the main directory and also 
                # in the backup
                clean(versions,config["limit"])
                # open the latest version of the product
            os.system(f"xdg-open {versions[0][0]} &")


def flagparse(argv: List[str]) -> Flags:
    flags = Flags()
    if len(argv) == 1: return flags
    num_positional_args: int = 0
    i: int = 1
    while i < len(argv):
        if argv[i][0] != '-':
            if num_positional_args == 0:
                try: flags.action = Action(argv[i])
                except ValueError: flags.product_path = argv[i]
            else:
                flags.product_path = argv[i]
            num_positional_args += 1
        elif argv[i] == "-h" or argv[i] == "--help":
            flags.help = True
        elif argv[i] == "-v" or argv[i] == "--version":
            flags.version = True
        elif argv[i] == "-o" or argv[i] == "--only-open":
            flags.only_open = True
        elif argv[i] == "-d" or argv[i] == "--output-directory":
            flags.output_dir = argv[i+1]
            i += 1
        elif argv[i] == "-f" or argv[i] == "--format":
            flags.stamp_format = argv[i+1]
            i += 2
            continue
        else:
            match flags.action:
                case Action.BACKUP:
                    try: flags.backup_action = BackupAction(argv[i])
                    except ValueError: pass
                case Action.DESKTOP:
                    if argv[i] == "--remove":
                        flags.desktop_remove = True
        i += 1
    match flags.action:
        case Action.RELEASE:
            flags.action = Action.BACKUP
            flags.backup_action = BackupAction.RELEASE
        case Action.DESKTOP:
            if not hasattr(flags,"desktop_remove"):
                flags.desktop_remove = False
    return flags

"""
Converts a 'pattern' with a '%V' in it to a regular expression that matches
any filename with a version number in place of the '%V'. Also converts any
'%%' to a literal '%' so '%%V' will be matched to a literal '%V' in the
pattern
    @param pattern: The given 'pattern'
"""
def pat_to_regex(pattern: str) -> Pattern:
    new_pattern: str = ""
    is_escaped: bool = False
    for char in pattern:
        if char == "%" and not is_escaped:
            is_escaped = True
            continue
        if is_escaped:
            is_escaped = False
            if char == "V":
                new_pattern += r"(\d+)"
                continue
        if char == ".":
            new_pattern += r"\."
            continue
        new_pattern += char
    return re.compile(new_pattern)

"""
Gets the names & versions of all the product files in the current working 
directory, sorted in reverse order of versions (so the latest version is
first on the list)
    @param regex: The regular expression used to identify product files,
        i.e. the output of pat_to_regex
    @return A list, whose entries are tuples of the form
        (filename, product version of filename)
"""
def get_versions(regex: Pattern) -> Product:
    match: Match[str] | None
    versions: Product = []
    for filename in os.listdir():
        match = regex.fullmatch(filename)
        if  match == None:
            continue
        versions.append( (filename, int(match.group(1))) )
    versions.sort(key=lambda product_file: product_file[1], reverse=True)
    return versions

"""
Deletes the oldest versions of the product until only a given number are
left. Must be run from within the directory of the files you wish to delete
    @param versions: The filenames of the various product versions, paired
        with their respective versions. The output of get_versions
    @param limit: The number of versions to leave behind
"""
def clean(versions: Product, limit: int):
    for i in range(limit,len(versions)):
        os.remove(versions[i][0])

"""
Selects every nth version of the product and copies it to a given
destination. "nth version" here means that the *version number* is divisble
by n. Also deletes older versions in copies directory until only a given 
number are left, using the clean function.
    @param versions: The versions of the product; the output of get_versions
    @param regex: the regex used to identify a product file
    @param config: the section of the configuration used for sample backups.
        It has the following values:
            destination: the given directory above
            frequency: the value of n
            limit: the maximum number of backups to leave behind
"""
def backup_sample(versions: Product, regex: Pattern, config: dict[str,Any]):
    for version in versions:
        if version[1] % config["frequency"] == 0:
            shutil.copy2(version[0],config["destination"])
    orig_dir: str = os.getcwd()
    os.chdir(config["destination"])
    clean(get_versions(regex),config["limit"])
    os.chdir(orig_dir)

"""
Makes a copy of a given file with a date-time-stamp added to the file's name.
Note that the stamp is added before the last extension, i.e. before the last
'.' character.
    @param file: The path to the given file.
    @param format: The format of the date-time-stamp.
    @param now: The datetime to be used for the stamp. Defaults to the
        present.
    @param dst: The directory the copy should be placed in. Defaults to the
        pwd.
    @return: The new (absolute) file path.
"""
def date(
        file: str,
        format: str,
        now: datetime=datetime.now(),
        dst: str="?"
) -> str:
    if dst == "?":
        dst = os.path.dirname(file)
    dst = os.path.abspath(dst)  # note this removes any '/' at the end
    basename: str = os.path.basename(file)
    ext_index: int = basename.rfind(".")
    format = now.strftime(format)
    new_file: str
    if ext_index == -1:
        new_file = f"{dst}/{basename}{format}"
    else:
        new_file = f"{dst}/{basename[:ext_index]}{format}{basename[ext_index:]}"
    if os.path.isdir(file):
        shutil.copytree(file,new_file)
    else:
        shutil.copy2(file,new_file)
    return new_file

def prompt(question: str, default: str="") -> str:
    print(f"\x1b[1m{question}\x1b[0m")
    print("\x1b[1m> \x1b[0m", end="")
    answer: str = input()
    return answer if answer else default

def prompt_yn(question: str, default_yes: bool=True) -> bool:
    answer: str
    if default_yes:
        print(f"\x1b[1m{question} (Y/n)\n> \x1b[0m",end="")
        answer = input()
        if answer:
            return answer.lower() not in ["no","n"]
        else:
            return True
    else:
        print(f"\x1b[1m{question} (y/N)\n> \x1b[0m",end="")
        answer = input()
        if answer:
            return answer.lower() in ["yes","y"]
        else:
            return False

"""
Creates  or overwrites a desktop file for the product at a given path
with a given configuration.
    @param product_path: The given path.
    @param config: The product configuration. May or may not have a
        desktop file configuration. If it has no such section, prompts 
        the user for the information needed to make one, and then adds
        the relevant settings to the config file.
"""
def add_desktop_file(product_path: str, config: dict[str,Any]):
    if not os.path.exists(DESKTOP_FILES_LOC):
        os.mkdir(DESKTOP_FILES_LOC)
    if "desktop" in config:
        print(
            "Desktop file configuration exists -",
            "trying to make desktop file from that...",
            end="\n\n"
        )
    else:
        # prompt the user to make desktop config options
        config["desktop"] = dict()
        config["desktop"]["name"] = prompt("What do want the application to be called? ")
        config["desktop"]["description"] = prompt("Description (one line)")
        config["desktop"]["only_open"] = \
            prompt_yn("Skip cleaning when opening the app?",default_yes=False)
        # a formatted datetime is used here because
        #     a) it limits how long the datetime-stamp will be
        #     b) it could be useful for debugging later
        config["desktop"]["location"] = (
            DESKTOP_FILES_LOC
            + "/"
            + os.path.basename(product_path)
            + datetime.now().strftime("-%Y%m%d%H%M%S")
            + ".desktop"
        )
        config_file: TextIO = open(
            f"{product_path}/.phase",
            "a",
            encoding="utf8"
        )
        # write the newly made options to the config file
        config_file.write(textwrap.dedent(f"""
            [desktop]
            # Do not change this!
            location = '{config["desktop"]["location"]}'
            name = '{config["desktop"]["name"]}'
            description = '{config["desktop"]["description"]}'
            only_open = {str(config["desktop"]["only_open"]).lower()}
        """))
        config_file.close()
    if os.path.exists(config["desktop"]["location"]):
        conflicting_file: TextIO = open(
            config["desktop"]["location"],"r",encoding="utf8"
        )
        for line in conflicting_file:
            if line.startswith("Exec="):
                print(textwrap.dedent(f"""\
                    A desktop file for this product seems to exist already.
                    When opened it runs:
                    -> {line[5:]}
                    If you want to overwrite this file, run
                    -> phase desktop --remove
                    to get rid of the existing file, and then try again.
                """))
                conflicting_file.close()
                sys.exit(1)
        conflicting_file.close()
    desktop_file: TextIO = open(
        config["desktop"]["location"],
        "w",
        encoding="utf8"
    )
    desktop_file.write(textwrap.dedent(f"""\
        [Desktop Entry]
        Name={config["desktop"]["name"]}
        GenericName={config["desktop"]["description"]}
        Exec=phase {"--only-open " if config["desktop"]["only_open"] else ""}{product_path}
        Type=Application
        Icon=Phase
    """))
    desktop_file.close()

def remove_desktop_file(product_path,config: dict[str,Any]):
    if "desktop" not in config:
        print(textwrap.dedent("""
            This product has no desktop entry file.
            To make one, run
            -> phase desktop --add
        """))
        sys.exit(1)
    # remove the desktop file itself
    os.remove(config["desktop"]["location"])
    # remove the desktop config
    # the line range we want to remove
    start_index: int = -1
    end_index: int = -1
    new_config: List[str] = []
    config_file: TextIO
    with open(f"{product_path}/.phase","r",encoding="utf8") as config_file:
        for line in config_file:
            new_config.append(line)
    for i in range(len(new_config)):
        if new_config[i].strip() == "[desktop]":
            start_index = i
            # get rid of any generated whitespace
            if i > 0 and new_config[i-1].strip() == "":
                start_index -= 1
        # see if we've reached another table
        if start_index >= 0 and \
                new_config[i][0] == "[" and new_config[i][1:8] != "desktop":
            end_index = i
    if end_index < 0 and start_index >= 0:
        end_index = len(new_config)
    with open(f"{product_path}/.phase","w",encoding="utf8") as config_file:
        for i in range(len(new_config)):
            if start_index <= i and i < end_index:
                continue
            config_file.write(new_config[i])

def initialise(product_path: str):
    if os.path.exists(product_path + "/.phase"):
        print("This directory already contains a .phase file!")
        print("Delete it if you wish to continue")
        sys.exit(1)
    config: dict[str,Any] = dict()
    config["pattern"] = prompt("What pattern should product files have?")
    config["limit"] = prompt(
        "How many versions should be left in the main directory at a " +
        "time?\nDefault is 11",
        default="11"
    )
    config["backup"] = dict()
    config["backup"]["sample"] = dict()
    config["backup"]["release"] = dict()
    config["backup"]["all"] = dict()
    config["backup"]["sample"]["frequency"] = prompt(
        "How often should a backup be made?\n" + 
        "Your answer should be a number N, and a backup will then be made " +
        "every Nth version. Default is 5",
        default="5"
    )
    config["backup"]["sample"]["destination"] = prompt(
        "Where should those backups go? (path can be relative)\n" + 
        "Default is ./backups",
        default="./backups"
    )
    os.makedirs(config["backup"]["sample"]["destination"],exist_ok=True)
    config["backup"]["sample"]["limit"] = prompt(
        "How many backups should be kept around at a time?\n" +
        "Default is 11",
        default="11"
    )
    config["backup"]["release"]["format"] = prompt(
        "You can also make copies of versions with a date/time stamp " +
        "attached, called \"Releases\".\n What format do you want those " +
        "date/time stamps to be in?\n" +
        "Default is _%Y%m%d",
        default="_%Y%m%d"
    )
    config["backup"]["release"]["destination"] = prompt(
        "Where do you want those Releases to go? (path can be relative)\n" +
        "Default is ./releases",
        default="./releases"
    )
    os.makedirs(config["backup"]["release"]["destination"],exist_ok=True)
    config["backup"]["all"]["cmd"] = prompt(
        "What is a shell command you can use to backup this entire " +
        "directory?\n If you don't have/want one, just leave this blank",
        default="echo \"No backup all command assigned\""
    )
    config_file: TextIO = open(f"{product_path}/.phase","w",encoding="utf8")
    config_file.write(textwrap.dedent(f"""\
        pattern = '{config["pattern"]}'
        limit = {config["limit"]}
        
        [backup]
        [backup.sample]
        frequency = {config["backup"]["sample"]["frequency"]}
        destination = '{config["backup"]["sample"]["destination"]}'
        limit = {config["backup"]["sample"]["limit"]}
        [backup.release]
        format = '{config["backup"]["release"]["format"]}'
        destination = '{config["backup"]["release"]["destination"]}'
        [backup.all]
        cmd = '{config["backup"]["all"]["cmd"]}'
    """))
    config_file.close()
    create_desktop: bool = prompt_yn(
        "Create a desktop entry file?\n This will allow you to open " +
        "the latest version of the product from an app launcher",
        default_yes=False
    )
    if create_desktop:
        add_desktop_file(product_path,config)
    print("---\nInitialisation Complete!")
    


if __name__ == "__main__": main()

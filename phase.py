#!/bin/env python3

import os
import shutil
import re
import sys
import tomllib
from typing import Pattern, Match, List, Tuple, Any, Union, TextIO
from enum import Enum
import enum
from datetime import datetime


type Version = int
type Product = List[Tuple[str,Version]]

# Represents main action for phase to take; default is to open the latest
# version & do clean-up
@enum.unique
class Action(Enum):
    DEFAULT = "default"
    DATE = "date"
    BACKUP = "backup"
    RELEASE = "release"
    DESKTOP = "desktop"

@enum.unique
class BackupAction(Enum):
    ALL = "--all"
    RELEASE = "--release"
    SAMPLE = "--sample"

# Represents the options specified at the commandline by user, after being 
# parsed
class Flags():
    def __init__(self):
        self.action: Action = Action.DEFAULT
        self.help: bool = False
        self.only_open: bool = False
        self.product_path: str = os.getcwd()
        self.stamp_format: str = ""
        self.output_dir: str = os.getcwd()
        self.backup_action: BackupAction
        self.desktop_remove: bool

class ConfigError(Exception):
    product_path: str
    
def main():
    flags = flagparse(sys.argv)
    flags.product_path = os.path.abspath(flags.product_path)
    os.chdir(flags.product_path)
    if flags.help:
        print("Phase, v0.5\nThe Best Worst Version Control")
        exit()
    # load product configration
    config: Union[dict[str,Any],None] = None
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
            if not config or not versions: raise ConfigError
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
        case _:
            if not config or not versions: raise ConfigError
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
    shutil.copy2(file,new_file)
    return new_file

"""
Prompts the user with a given question and returns their answer.
"""
def prompt(question: str) -> Any:
    print(f"{question}: ")
    return input

def add_desktop_file(product_path: str):
    app_name: str = prompt("What do want the application to be called?")
    desktop_filename: str = app_name.lower().replace(" ","-")
    description: str = prompt("Description (one line)")
    only_open: bool = \
        prompt("Skip cleaning when opening the app? (y/n)") == "y"
    desktop_file: TextIO = open(
        f"{os.getenv("HOME")}/.local/share/applications/{desktop_filename}.desktop",
        "w",
        encoding="utf8"
    )
    desktop_file.write(
        f"""
        [Desktop Entry]
        Name={app_name}
        GenericName={description}
        Exec=phase {"--only-open " if only_open else ""}{product_path}
        Type=Application
        """
    )


if __name__ == "__main__": main()

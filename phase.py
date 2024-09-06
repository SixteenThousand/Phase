#!/bin/env python3

import os
import shutil
import re
import sys
import tomllib
from typing import Pattern, Match, List, Tuple, Any
from enum import Enum, unique
from datetime import datetime


type Version = int
type Product = List[Tuple[str,Version]]

# Represents main action for phase to take; default is to open the atest
# version & do clean-up
@unique
class Action(Enum):
    DEFAULT = "default"
    DATE = "date"

# Represents the options specified at the commandline by user, after being 
# parsed
class Flags():
    def __init__(self):
        self.action: Action = Action.DEFAULT
        self.help: bool = False
        self.only_open: bool = False
        self.product_path: str = os.getcwd()
        self.stamp_format: str = "%y%m%d-%H%M%S"
    
def main():
    flags = flagparse(sys.argv)
    if flags.help:
        print("Phase, v0.4\nThe Best Worst Version Control")
        exit()
    match flags.action:
        case Action.DATE:
            new_name: str = date(
                flags.product_path,
                flags.stamp_format,
                datetime.now()
            )
            print(f"{flags.product_path} -> {new_name}")
        case _:
            flags.product_path = os.path.abspath(flags.product_path)
            # start actually doing things
            os.chdir(flags.product_path)
            # load product configration
            with open("./.phase","rb") as fp:
                config = tomllib.load(fp)
            config["regex"] = pat_to_regex(config["pattern"])
            versions: Product = get_versions(config["regex"])
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


"""
Parses the arguments passed at the command line into a Flags object.
"""
def flagparse(argv: List[str]) -> Flags:
    flags = Flags()
    if len(argv) == 1: return flags
    num_positional_args: int = 0
    for arg in argv[1:]:
        if arg == "-h" or arg == "--help":
            flags.help = True
        if arg == "-o" or arg == "--only-open":
            flags.only_open = True
        if arg.startswith("-f") or arg.startswith("--format"):
            flags.stamp_format = arg.partition("=")[2]
        if arg[0] != '-':
            if  num_positional_args == 0:
                try: flags.action = Action(arg)
                except ValueError: flags.product_path = arg
            else:
                flags.product_path = arg
            num_positional_args += 1
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


if __name__ == "__main__": main()

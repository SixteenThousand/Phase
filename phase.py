#!/bin/env python3

import os
import shutil
import re
import argparse
import tomllib
from typing import Pattern, Match, List, Tuple, Any


type Version = int
type Product = List[Tuple[str,Version]]


def main():
    # parse command line flags
    parser = argparse.ArgumentParser(
        description = "phase, v0.1\nA tool for dumb file versioning",
        usage = "",
        epilog = ""
    )
    parser.add_argument(
        "product_path",
        nargs="?",
        default=os.getcwd()
    )
    args = parser.parse_args()
    args.product_path = os.path.abspath(args.product_path)
    # start actually doing things
    os.chdir(args.product_path)
    # load product configration
    global config
    with open("./.phase","rb") as fp:
        config = tomllib.load(fp)
    config["regex"] = pat_to_regex(config["pattern"])
    versions: Product = get_versions(config["regex"])
    # make backups
    backup_sample(
        versions,
        config["regex"],
        config["backup"]["sample"],
    )
    # clean up old versions, both in the main directory and also in the backup
    clean(versions,config["limit"])
    # open the latest version of the product
    os.system(f"xdg-open {versions[0][0]}")


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


if __name__ == "__main__": main()

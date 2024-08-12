#!/bin/env python3

import os
import shutil
import argparse
import tomllib
from typing import Match, List, Tuple


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
        default="."
    )
    args = parser.parse_args()
    # go to the product directory
    os.chdir(args.product_path)
    # load product configration
    global config
    with open("./.phase","rb") as fp:
        config = tomllib.load(fp)
    versions: Product = get_versions(pat_to_regex(config["pattern"]))
    for i in range(config["max"],len(versions)):
        os.system("rm -r "+versions[i][0])
    os.system("xdg-open "+versions[0][0])


"""
Converts a 'pattern' with a '%V' in it to a regular expression that matches
any filename with a version number in place of the '%V'. Also converts any
'%%' to a literal '%' so '%%V' will be matched to a literal '%V' in the
pattern
    @param pattern: The given 'pattern'
"""
def pat_to_regex(pattern: str) -> str:
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
            new_pattern += r"\\."
            continue
        new_pattern += char
    return new_pattern

"""
Gets the names & versions of all the product files in the current working 
directory, sorted in reverse order of versions (so the latest version is
first on the list)
    @param regex: The regular expression used to identify product files,
        i.e. the output of pat_to_regex
    @return A list, whose entries are tuples of the form
        (filename, product version of filename)
"""
def get_versions(regex) -> Product:
    match: Match
    versions: Product = []
    for filename in os.listdir():
        match = regex.fullmatch(filename)
        if  match == None:
            continue
        versions.append( (filename, int(match.group(1))) )
    versions.sort(key=lambda product_file: product_file[1], reverse=True)
    return versions


if __name__ == "__main__": main()

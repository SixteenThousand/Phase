#!/bin/env python3

import os
import shutil
import argparse
import tomllib
from typing import Pattern


type Product = dict[str,int]


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
    versions: Product = get_product_versions(pat_to_regex(config["pattern"]))


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
directory.
    @param regex: The regular expression used to identify product files,
        i.e. the output of pat_to_regex
    @return A dictionary with filenames as keys and version numbers as 
        values
"""
def get_product_versions(regex) -> Product:
    match: Pattern
    versions: Product = dict()
    for filename in os.listdir():
        match = regex.fullmatch(filename)
        if  match == None:
            continue
        versions[filename] = int(match.group(1))
    return versions



if __name__ == "__main__": main()

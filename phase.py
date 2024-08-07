#!/bin/env python3

import os
import shutil
import sys
import argparse
import tomllib


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
    config["pattern"] = process_escapes(config["pattern"])


"""
Converts a 'pattern' with a '%V' in it to a regular expression that matches
any filename with a version number in place of the '%V'. Also converts any
'%%' to a literal '%' so '%%V' will be matched to a literal '%V' in the
pattern
    @param pattern: the given 'pattern'
"""
def process_escapes(pattern: str) -> str:
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


if __name__ == "__main__": main()

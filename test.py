import phase
import re
import os
from pathlib import Path
import pprint

PROJ_ROOT = os.getcwd()
DATA_DIR = PROJ_ROOT + "/test-data"


def main():
    assert pat_to_regex_test()
    assert get_versions_test()
    print("All tests passed!")


def pat_to_regex_test() -> bool:
    examples = {
        "boring_stuff_v%V.txt": re.compile(r"boring_stuff_v(\d+)\.txt"),
        "TooMany%%VpercentSigns%V.py": 
            re.compile(r"TooMany%VpercentSigns(\d+)\.py"),
    }
    for filename in examples:
        result = phase.pat_to_regex(filename)
        if result != examples[filename]:
            print(f"Example {filename} failed!")
            print(f"    result: {result}")
            print(f"    expected: {examples[filename]}")
            return False
    return True

def get_versions_test() -> bool:
    examples = [
        {
            "comment": "no padding",
            "regex": re.compile(r"boring_stuff_v(\d+)\.ods"),
            "seed_files":
                [f"boring_stuff_v{i}.ods" for i in range(1,6)] +
                ["dud", "oring_stuff_v1.ods", "boring_stuff_v5Xods"],
            "product_files":
                [(f"boring_stuff_v{i}.ods",i) for i in range(5,0,-1)],
        },
        {
            "comment": "zero-padding",
            "regex": re.compile(r"boring_stuff_v(\d+)\.ods"),
            "seed_files":
                [f"boring_stuff_v{i:02}.ods" for i in range(1,6)] +
                ["dud", "oring_stuff_v1.ods", "boring_stuff_v5Xods"],
            "product_files":
                [(f"boring_stuff_v{i:02}.ods",i) for i in range(5,0,-1)],
        },
    ]
    os.chdir(DATA_DIR)
    for example in examples:
        # re-seed DATA_DIR
        os.system(f"rm -r {DATA_DIR}/*")
        for filename in example["seed_files"]:
            Path(filename).touch(exist_ok=False)
        result = phase.get_versions(example["regex"])
        if result != example["product_files"]:
            print(f"Fail: {example["comment"]}")
            print(f"    got: {pprint.pformat(result)}")
            print(f"    exp: {pprint.pformat(example["product_files"])}")
            return False
    return True

def clean_test() -> bool:
    os.chdir(DATA_DIR)
    ex_regex = re.compile(r"thingy-ma-jig_v(\d+)\.pdf")
    ex_filename_prefix = "thingy-ma-jig_v"
    ex_filename_suffix = ".pdf"
    ex_limit = 11
    ex_nonmatching_filenames = [
        "dud",
        "thingy_ma_jig_v9.pdf",
        "thingy-ma-jig_v.pdf",
        "thingy-ma-jig_v3Xpdf",
    ]
    examples = [
        {
            "comment": "do nothing",
            "seed":
                [ex_filename_prefix+str(i)+ex_filename_suffix
                     for i in range(1,6)] + ex_nonmatching_filenames,
            "expected":
                [ex_filename_prefix+str(i)+ex_filename_suffix
                     for i in range(1,6)] + ex_nonmatching_filenames,
        },
        {
            "comment": "get rid of the earliest versions",
            "seed":
                [ex_filename_prefix+str(i)+ex_filename_suffix
                    for i in range(1,21)] + ex_nonmatching_filenames,
            "expected":
                [ex_filename_prefix+str(i)+ex_filename_prefix
                    for i in range(10,21)],
        },
        {
            "comment": "offset",
            "seed":
                [ex_filename_prefix+str(i)+ex_filename_suffix
                    for i in range(45,60)] + ex_nonmatching_filenames,
            "expected":
                [ex_filename_prefix+str(i)+ex_filename_prefix
                    for i in range(49,60)],
        },
        {
            "comment": "exactly at the limit!",
            "seed":
                [ex_filename_prefix+str(i)+ex_filename_suffix
                 for i in range(1,12)] + ex_nonmatching_filenames,
            "expected":
                [ex_filename_prefix+str(i)+ex_filename_suffix
                    for i in range(1,12)],
        },
    ]
                
            


if __name__ == "__main__": main()

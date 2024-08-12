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
    os.chdir(DATA_DIR)
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
    


if __name__ == "__main__": main()

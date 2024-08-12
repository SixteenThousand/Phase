import phase
import os
from pathlib import Path

PROJ_ROOT = os.getcwd()
DATA_DIR = "./test-data"


def main():
    assert pat_to_regex_test()
    seed()
    print("All tests passed!")


class Example():
    def __init__(self,comment,config_file,regex,seed_files,product_files):
        self.comment = comment
        self.config_file = config_file
        self.regex = regex
        self.seed_files = seed_files
        self.product_files = product_files
    
    def seed(self):
        os.chdir(DATA_DIR)
        os.system("rm -r ./*")
        for filename in self.seed_files:
            Path(filename).touch(exist_ok=False)

examples = [
    Example(
        comment = "nothing needs to be done",
        config_file = """
        pattern = "boring_stuff_v%V.ods"
        limit = 11
        """,
        regex = r"boring_stuff_v(\d+)\.ods",
        seed_files = [f"boring_stuff_v{i}.ods" for i in range(1,6)] +
            ["dud", "oring_stuff_v1.ods", "boring_stuff_v5Xods"],
        product_files = [(f"boring_stuff_v{i}.ods",i) for i in range(5,0,-1)],
    ),
    Example(
        comment = "nothing + zero-padding",
        config_file = """
        pattern = "boring_stuff_v%V.ods"
        limit = 11
        """,
        regex = r"boring_stuff_v(\d+)\.ods",
        seed_files = [f"boring_stuff_v{i:02}.ods" for i in range(1,6)] +
            ["dud", "oring_stuff_v1.ods", "boring_stuff_v5Xods"],
        product_files = [(f"boring_stuff_v{i}.ods",i) for i in range(5,0,-1)],
    ),
    Example(
        comment = "nothing + offset",
        config_file = """
        pattern = "boring_offset_v%V.ods"
        limit = 11
        """,
        regex = r"boring_stuff_v(\d+)\.ods",
        seed_files = [f"boring_stuff_v{i}.ods" for i in range(50,56)] +
            ["dud", "oring_stuff_v1.ods", "boring_stuff_v5Xods"],
        product_files = [(f"boring_stuff_v{i}.ods",i) for i in range(55,49,-1)],
    ),
    Example(
        comment = "some files need to be removed",
        config_file = """
        pattern = "curious_stuff_v%V.ods"
        limit = 11
        """,
        regex = r"curious_stuff_v(\d+)\.ods",
        seed_files = [f"curious_stuff_v{i}.ods" for i in range(1,21)],
        product_files = [f"curious_stuff_v{i}.ods" for i in range(20,9,-1)],
    ),
    Example(
        comment = "there are exactly right number of versions",
        config_file = """
        pattern = "fascinating_stuff_v%V.ods"
        limit = 11
        """,
        regex = r"fascinating_stuff_v(\d+)\.ods",
        seed_files =
            [f"fascinating_stuff_v{i:02}.ods" for i in range(1,12)],
        product_files = [f"fascinating_stuff_v{i}.ods" for i in range(11,0)],
    ),
]


def pat_to_regex_test() -> bool:
    examples = {
        "boring_stuff_v%V.txt": r"boring_stuff_v(\d+)\\.txt",
        "TooMany%%VpercentSigns%V.py": r"TooMany%VpercentSigns(\d+)\\.py",
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
    seed()
    examples = {
        r"boring_stuff_v(\d+)\.ods":
            [(f"boring_stuff_v{i}.ods",i) for i in range(1,6)],
        r"boring_padded_v(\d)\.ods":
            [(f"boring_padded_v{i:03}.pdf",i) for i in range(1,6)],
        r"boring_offset_v(\d)\.ods":
            [(f"boring_padded_v{i+10}.pdf",i) for i in range(1,6)],
        r"sometimes_padded_v(\d+)\.pdf":
            [(f"sometimes_padded_v{i:02},i) for i in range(1,21)],
        r"interesting_stuff_v(\d+)\.
    }
    


if __name__ == "__main__": main()

import phase
import os
from pathlib import Path

DATA_DIR = "./test-data"


def main():
    assert pat_to_regex_test()
    seed()
    print("All tests passed!")

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

def seed():
    os.chdir(DATA_DIR)
    for file in os.listdir("."):
        os.system("rm -r "+file)
    for i in range(1,6):
        Path(f"boring_stuff_v{i}.ods").touch(exist_ok=False)
        Path(f"boring_padded_v{i:03}.ods").touch(exist_ok=False)
    for i in range(1,21):
        Path(f"interesting_stuff_v{i}.pdf").touch(exist_ok=False)
        Path(f"interesting_padded_v{i:03}.pdf").touch(exist_ok=False)
        Path(f"sometimes_padded_v{i:02}.pdf").touch(exist_ok=False)
    for i in range(1,12):
        Path(f"fascinating_stuff_v{i}").touch(exist_ok=False)
        Path(f"fascinating_padded_v{i:03}").touch(exist_ok=False)
    for i in range(1,21):
        os.mkdir(f"interesting_dir_v{i}")
    Path("dud").touch(exist_ok=False)
    Path("oring_stuff_1.ods").touch(exist_ok=False)
    Path("boring_stuff_v1Xods").touch(exist_ok=False)
    Path("boring_stuffv1Xods").touch(exist_ok=False)


if __name__ == "__main__": main()

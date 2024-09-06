import phase
import re
import os
from pathlib import Path
import pprint
from typing import List, Tuple, Any, Pattern
from datetime import datetime

PROJ_ROOT = os.getcwd()
DATA_DIR = PROJ_ROOT + "/test-data"


def main():
    assert pat_to_regex_test()
    assert get_versions_test()
    assert clean_test()
    assert backup_sample_test()
    assert flagparse_test()
    assert date_test()
    print("All tests passed!")


def pat_to_regex_test() -> bool:
    examples: dict[str,Pattern] = {
        "boring_stuff_v%V.txt": re.compile(r"boring_stuff_v(\d+)\.txt"),
        "TooMany%%VpercentSigns%V.py": 
            re.compile(r"TooMany%VpercentSigns(\d+)\.py"),
    }
    for filename in examples:
        result: Pattern = phase.pat_to_regex(filename)
        if result != examples[filename]:
            print(f"Example {filename} failed!")
            print(f"    result: {result}")
            print(f"    expected: {examples[filename]}")
            return False
    return True

def get_versions_test() -> bool:
    examples: List[dict[str,Any]] = [
        {
            "comment": "no padding",
            "regex": re.compile(r"boring_stuff_v(\d+)\.ods"),
            "seed_dirs": [],
            "seed_files":
                [f"boring_stuff_v{i}.ods" for i in range(1,6)] +
                ["dud", "oring_stuff_v1.ods", "boring_stuff_v5Xods"],
            "product_files":
                [(f"boring_stuff_v{i}.ods",i) for i in range(5,0,-1)],
        },
        {
            "comment": "zero-padding",
            "regex": re.compile(r"boring_stuff_v(\d+)\.ods"),
            "seed_dirs": [],
            "seed_files":
                [f"boring_stuff_v{i:02}.ods" for i in range(1,6)] +
                ["dud", "oring_stuff_v1.ods", "boring_stuff_v5Xods"],
            "product_files":
                [(f"boring_stuff_v{i:02}.ods",i) for i in range(5,0,-1)],
        },
        {
            "comment": "product is a directory",
            "regex": re.compile(r"boring_dir_v(\d+)"),
            "seed_dirs":
                [f"boring_dir_v{i}" for i in range(1,13)] +
                    ["dud_dir","boring_dir_vd"],
            "seed_files": [],
            "product_files":
                [(f"boring_dir_v{i}",i) for i in range(12,0,-1)],
        },
        {
            "comment": "product is a directory or a file",
            "regex": re.compile(r"project_thing_v(\d+)"),
            "seed_dirs": [f"project_thing_v{i}" for i in range(1,5)],
            "seed_files": [f"project_thing_v{i}" for i in range(5,10)],
            "product_files":
                [(f"project_thing_v{i}",i) for i in range(9,0,-1)],
        },
    ]
    os.chdir(DATA_DIR)
    for example in examples:
        # re-seed DATA_DIR
        os.system(f"rm -r {DATA_DIR}/*")
        for filename in example["seed_files"]:
            Path(filename).touch(exist_ok=False)
        for dirname in example["seed_dirs"]:
            os.mkdir(dirname)
        result: phase.Product = phase.get_versions(example["regex"])
        if result != example["product_files"]:
            print(f"Fail: {example["comment"]}")
            print(f"    got: {pprint.pformat(result)}")
            print(f"    exp: {pprint.pformat(example["product_files"])}")
            return False
    return True

def clean_test() -> bool:
    ex_filename_prefix: str = "thingy-ma-jig_v"
    ex_filename_suffix: str = ".pdf"
    ex_limit: int = 11
    ex_nonmatching_filenames: List[str] = [
        "dud",
        "thingy_ma_jig_v9.pdf",
        "thingy-ma-jig_v.pdf",
        "thingy-ma-jig_v3Xpdf",
    ]
    def ex_filename(version: phase.Version):
        return f"{ex_filename_prefix}{version}{ex_filename_suffix}"
    examples: List[dict[str,Any]] = [
        {
            "comment": "do nothing",
            "versions": [(ex_filename(i),i) for i in range(5,0,-1)],
            "expected": [ex_filename(i) for i in range(1,6)] +
                ex_nonmatching_filenames,
        },
        {
            "comment": "get rid of the earliest versions",
            "versions": [(ex_filename(i),i) for i in range(20,0,-1)],
            "expected": [ex_filename(i) for i in range(10,21)] +
                ex_nonmatching_filenames,
        },
        {
            "comment": "offset",
            "versions": [(ex_filename(i),i) for i in range(59,44,-1)],
            "expected": [ex_filename(i) for i in range(49,60)] +
                ex_nonmatching_filenames,
        },
        {
            "comment": "exactly at the limit!",
            "versions": [(ex_filename(i),i) for i in range(11,0,-1)],
            "expected": [ex_filename(i) for i in range(1,12)] +
                ex_nonmatching_filenames,
        },
        {
            "comment": "clean a sample backup directory",
            "versions": [(ex_filename(5*i),5*i) for i in range(15,0,-1)],
            "expected": [ex_filename(5*i) for i in range(5,16)] +
                ex_nonmatching_filenames,
        },
    ]
    os.chdir(DATA_DIR)
    for example in examples:
        # remove files from previous tests
        os.system(f"rm -r {DATA_DIR}/*")
        # seed DATA_DIR with product files
        for version in example["versions"]:
            Path(version[0]).touch(exist_ok=False)
        # seed DATA_DIR with files phase should not touch
        for filename in ex_nonmatching_filenames:
            Path(filename).touch(exist_ok=False)
        phase.clean(example["versions"],ex_limit)
        expected_dir_contents: List[str] =  sorted(example["expected"])
        actual_dir_contents: List[str] = sorted(os.listdir()) 
        if actual_dir_contents != expected_dir_contents:
            print(f"Fail: {example["comment"]}")
            print(f"  got: {pprint.pformat(actual_dir_contents)}")
            print(f"  exp: {pprint.pformat(expected_dir_contents)}")
            return False
    return True

def backup_sample_test() -> bool:
    # set up a test case
    ex_versions: List[Tuple[str,phase.Version]] = [
        (f"some_thing_v{i}.pdf",i) for i in range(111,96,-1)
    ]
    ex_regex: Pattern = re.compile(r"some_thing_v(\d+)\.pdf")
    ex_backup_names: List[str] = [f"some_thing_v{i*5}.pdf" for i in range(3,20)]
    ex_backup_sample_config = {
        "frequency": 5,
        "destination": "./regular_backups",
        "limit": 10,
    }
    # expected files to be left in the sample backups directory
    ex_backups_expected: List[str] = sorted(
        [f"some_thing_v{i*5}.pdf" for i in range(22,12,-1)]
    )
    # expected files to be left in the main directory
    ex_main_expected: List[str] = sorted(
        [version[0] for version in ex_versions] +
            [ex_backup_sample_config["destination"][2:]]
    )
    # seed DATA_DIR accordingly
    os.system(f"rm -r {DATA_DIR}/*")
    os.chdir(DATA_DIR)
    os.mkdir(ex_backup_sample_config["destination"])
    for version in ex_versions:
        Path(version[0]).touch(exist_ok=False)
    for backup_name in ex_backup_names:
        Path(
            f"{ex_backup_sample_config["destination"]}/{backup_name}"
        ).touch(exist_ok=False)
    # run the function
    phase.backup_sample(ex_versions,ex_regex,ex_backup_sample_config)
    # check we have got the right backups & that the backups directory has 
    # been cleaned correctly
    backups_result: List[str] = sorted(
        os.listdir(ex_backup_sample_config["destination"])
    )
    if backups_result != ex_backups_expected:
        print("Fail: backups gone wrong")
        print(f"  got: {pprint.pformat(backups_result)}")
        print(f"  exp: {pprint.pformat(ex_backups_expected)}")
        return False
    # check that nothing has been changed in the main product directory
    main_result: List[str] = sorted(os.listdir("."))
    if main_result != ex_main_expected:
        print("Fail: sample backups changes main versions")
        print(f"    got: {pprint.pformat(main_result)}")
        print(f"    exp: {pprint.pformat(ex_main_expected)}")
        return False
    return True

def flagparse_test() -> bool:
    has_not_erred: bool = True
    def new_flags(attrs: dict[str,Any]):
        res = phase.Flags()
        for key,val in attrs.items():
            setattr(res,key,val)
        return res
    tcases: List[Tuple[List[str],phase.Flags]] = [
        (
            [],
            new_flags({})
        ),
        (
            ["-o"],
            new_flags({
                "only_open": True,
            })
        ),
        (
            ["--only-open"],
            new_flags({
                "only_open": True,
            })
        ),
        (
            ["-o","/home/username/Documents/Important-Thing"],
            new_flags({
                "only_open": True,
                "product_path": "/home/username/Documents/Important-Thing",
            })
        ),
        (
            ["/home/username/Documents/Important-Thing","-o"],
            new_flags({
                "only_open": True,
                "product_path": "/home/username/Documents/Important-Thing",
            })
        ),
        (
            ["date","-f=%y-%m-%d %H:%M:%S"],
            new_flags({
                "action": phase.Action.DATE,
                "stamp_format": "%y-%m-%d %H:%M:%S",
            })
        ),
        (
            ["date","--format=%y-%m-%d %H:%M:%S"],
            new_flags({
                "action": phase.Action.DATE,
                "stamp_format": "%y-%m-%d %H:%M:%S",
            })
        ),
        (
            ["-h"],
            new_flags({
                "help": True,
            })
        ),
        (
            ["--help"],
            new_flags({
                "help": True,
            })
        ),
    ]
    for tcase in tcases:
        got: phase.Flags = phase.flagparse(["phase"] + tcase[0])
        if got.__dict__ != tcase[1].__dict__:
            print("Fail: flagparse went kaput >>")
            print(f"    arg: {" ".join(tcase[0])}") 
            print(f"    got: {pprint.pformat(got.__dict__)}")
            print(f"    exp: {pprint.pformat(tcase[1].__dict__)}")
            print("<<")
            has_not_erred = False
    return has_not_erred

def date_test() -> bool:
    has_not_erred: bool = True
    tcases_now: datetime = datetime(2024,9,7,21,7,8)
    tcases: List[dict[str,Any]] = [
        {
            "input": ("some_file","_%y%m%d-%H%M%S",tcases_now),
            "seed": ["some_file"],
            "expected": "some_file_20240907-210708",
        },
        {
            "input": ("some_file_v23","_%y%m%d-%H%M%S",tcases_now),
            "seed": ["some_file_v23","some_file_v22","some_file_v24"],
            "expected": "some_file_v23_20240907-210708",
        },
        {
            "input": ("some_file_v34.pdf","_%y%m%d-%H%M%S",tcases_now),
            "seed": ["some_file_v34.pdf","some_file_v33.pdf","some_file_v35.pdf"],
            "expected": "some_file_v34_20240907-210708.pdf",
        },
        {
            "input": ("./some_file_v56.ods","_%y%m%d-%H%M%S",tcases_now),
            "seed": ["some_file_v56.ods"],
            "expected": "some_file_v56_20240907-210708.ods",
        },
        {
            "input": ("./some_file_v56.ods","-%H%S__%y--%m",tcases_now),
            "seed": ["some_file_v56.ods"],
            "expected": "some_file_v56-2108__2024--09.ods",
        },
    ]
    os.chdir(DATA_DIR)
    for tcase in tcases:
        os.system(f"rm -r {DATA_DIR}/*")
        for file in tcase["seed"]:
            Path(file).touch(exist_ok=False)
        new_file: str = phase.date(*tcase["input"])
        got_dircontents: List[str] = os.listdir()
        got_dircontents.sort()
        exp_dircontents: List[str] = tcase["seed"] + [new_file]
        exp_dircontents.sort()
        if tcase["expected"] != new_file:
            print("Fail: dating went wrong!")
            print(f"    arg: {pprint.pformat(tcase["input"])}")
            print(f"    got: {new_file}")
            print(f"    exp: {tcase["expected"]}")
            continue
        if got_dircontents != exp_dircontents:
            print("Fail: dating went wrong! >>")
            print(f"    arg: {pprint.pformat(tcase["input"])}")
            print(f"    got: {pprint.pformat(got_dircontents)}")
            print(f"    exp: {pprint.pformat(exp_dircontents)}")
            has_not_erred = False
    os.system(f"rm -r {DATA_DIR}/*")
    os.mkdir("some_directory")
    Path("./some_directory/some_file").touch(exist_ok=False)
    new_file = phase.date(
        "./some_directory/some_file",
        "_%y%m%d-%H%M%S",
        tcases_now
    )
    if new_file != "./some_directory/some_file_20240907-210708":
        print("Fail: dating naming went wrong when path used")
    if (os.listdir() != ["some_directory"] or
            os.listdir("some_directory") != [new_file]):
        print("Fail: dating changed file system incorrectly when path used")
    return has_not_erred
    

if __name__ == "__main__": main()

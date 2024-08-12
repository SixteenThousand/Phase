import phase

DATA_DIR = "./tests/test-data"
TEST_DIR = "./tests"


def main():
    assert pat_to_regex_test()
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


if __name__ == "__main__": main()

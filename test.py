import phase

DATA_DIR = "./tests/test-data"
TEST_DIR = "./tests"

def main():
    assert process_escapes_test()
    print("All tests passed!")


def process_escapes_test() -> bool:
    examples = {
        "boring_stuff_v%V.txt": r"boring_stuff_v(\d+)\\.txt",
        "TooMany%%VpercentSigns%V.py": r"TooMany%VpercentSigns(\d+)\\.py",
    }
    for filename in examples:
        result = phase.process_escapes(filename)
        if result != examples[filename]:
            print(f"Example {filename} failed!")
            print(f"    result: {result}")
            print(f"    expected: {examples[filename]}")
            return False
    return True

if __name__ == "__main__": main()

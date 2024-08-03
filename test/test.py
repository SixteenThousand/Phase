import phase
import shutil

DATA_DIR = "./tests/test-data"
TEST_DIR = "./tests"

def main():
    can_find_latest()


def can_find_latest():
    os.chdir(TEST_DIR)
    shutil.copy2("./open_latest_test.toml",DATA_DIR)


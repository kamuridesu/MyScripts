import sys
from pathlib import Path
from typing import Generator


def load(file: Path) -> Generator[dict[str, str], None, None]:
    if not file.exists():
        raise FileNotFoundError
    with open(file, "r") as f:
        while True:
            line = f.readline()
            if not line:
                break
            name, sha = line.split(": ")
            yield {name: sha}


def get_duplicated_items(files: Generator[dict[str, str], None, None]):
    visited_sha: list[str] = []
    duplicated: list[str] = []
    for file in files:
        for name, sha in file.items():
            if sha in visited_sha:
                print(f"Found duplicated file: {name}")
                duplicated.append(name)
                continue
            visited_sha.append(sha)
    return duplicated


def remove_duplicated(duplicated: list[str]):
    for file in duplicated:
        Path(file).unlink(True)


def main():
    if len(sys.argv) < 1:
        print(f"Usage: {sys.argv[0]} path/to/hashes_file.txt")
    root = sys.argv[1]
    files = load(Path(root))
    duplicated = get_duplicated_items(files)
    if input(f"Do you want to delete {len(duplicated)} files? [y/N]") == "y":
        remove_duplicated(duplicated)


if __name__ == "__main__":
    main()

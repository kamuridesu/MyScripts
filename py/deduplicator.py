import sys
from pathlib import Path
from typing import Generator


def load(file: Path) -> Generator[dict[str, str], None, None]:
    if not file.exists():
        raise FileNotFoundError
    with open(file, "r") as f:
        while True:
            line = f.readline().strip()
            if not line:
                break
            name, sha = line.split(": ")
            yield {name: sha}


def save(file: Path, data: dict[str, str]):
    buffer = ""
    for name, sha in data.items():
        buffer += f"{name}: {sha}\n"
    with open(file, "w") as f:
        f.write(buffer)


def get_duplicated_items(files: Generator[dict[str, str], None, None]):
    visited_sha: list[str] = []
    duplicated: list[str] = []
    validated = {}
    for file in files:
        for name, sha in file.items():
            if not Path(name).exists(follow_symlinks=True):
                print(f"[WARN] File {name} does not exists")
                continue
            if sha in visited_sha:
                print(f"[WARN] Found duplicated file: {name}")
                validated.update({name: sha})
                duplicated.append(name)
                continue
            visited_sha.append(sha)
            validated.update({name: sha})
    return duplicated, validated


def remove_duplicated(duplicated: list[str], validated: dict[str, str]):
    for file in duplicated:
        validated.pop(file)
        Path(file).unlink(True)


def main():
    if len(sys.argv) < 1:
        print(f"Usage: {sys.argv[0]} path/to/hashes_file.txt")
    root = sys.argv[1]
    files = load(Path(root))
    duplicated, validated = get_duplicated_items(files)
    if (
        len(duplicated) > 0
        and input(f"[WARN] Do you want to delete {len(duplicated)} files? [y/N]: ")
        == "y"
    ):
        remove_duplicated(duplicated, validated)
    save(Path(root), validated)


if __name__ == "__main__":
    main()

import getpass
import sys
from pathlib import Path

from pykeepass import Attachment, Entry, PyKeePass

type PathOrStr = Path | str

from dedup import dedup

FISH_HISTORY_PATH = Path.home() / ".local/share/fish/fish_history"

def read_fish_history() -> bytes:
    with open(FISH_HISTORY_PATH, "rb") as f:
        return f.read()


def save_fish_history(data: str):
    with open(FISH_HISTORY_PATH, "w") as f:
        f.write(data)


def load_database(db_path: PathOrStr) -> PyKeePass:
    password = getpass.getpass(f"Enter password to unlock {db_path}: ")
    return PyKeePass(db_path, password=password)


def create_entry(db: PyKeePass, path: list[str]) -> Entry:
    name = path[-1]
    group = db.root_group
    for p in path[:-1]:
        group = db.add_group(group, p)
    db.add_entry(group, name, "", "")
    db.save()
    print(f"Entry {'/'.join(path)} created, restart the script.")
    exit(0)


def load_entry(db: PyKeePass, path: list[str]) -> Entry:
    entry = db.find_entries(path=path)
    if entry is None:
        return create_entry(db, path)
    return entry


def attach_file(db: PyKeePass, path: list[str], data: bytes) -> Entry:
    entry = load_entry(db, path)

    attachment: list[Attachment] = entry.attachments
    if len(attachment) > 1:
        at = attachment[0]
        entry.delete_attachment(at)
        db.delete_binary(at.id)

    binary_id = db.add_binary(data)
    entry.add_attachment(binary_id, "fish_history")
    db.save()
    return entry


def read_attachment(db: PyKeePass, path: list[str]) -> bytes:
    entry = load_entry(db, path)
    attachment: list[Attachment] = entry.attachments
    if len(attachment) < 1:
        return b""
    return attachment[0].data


def main():
    name = sys.argv[0]
    if len(sys.argv) < 3:
        print(f"Usage: python {name} path-to-kdbx path/to/credential")
        exit(1)
    db_path = sys.argv[1]
    raw_path = sys.argv[2]

    path_list = [x for x in raw_path.split("/") if x != ""]

    print("Loading database...")
    db = load_database(db_path)
    print("Fetching attachment data...")
    attachment_data = read_attachment(db, path_list).decode()
    print("Reading fish history...")
    fish_history = read_fish_history().decode()
    print("Merging history...")
    concat_fish_history = dedup(f"{attachment_data}\n{fish_history}")

    print("Saving history...")
    save_fish_history(concat_fish_history)

    attach_file(db, path_list, concat_fish_history.encode())
    print("Done!")


if __name__ == "__main__":
    main()

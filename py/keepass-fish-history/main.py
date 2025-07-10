import getpass
import sys
import typing
from pathlib import Path

from pykeepass import Attachment, Entry, PyKeePass

type PathOrStr = Path | str
from dedup import dedup


class KeepassManager:
    def __init__(self, db_path: str, path: str) -> None:
        self.db = self.__load_database(db_path)
        self.path = [x for x in path.split("/") if x != ""]
        self.__entry: Entry | None = None

    @property
    def entry(self) -> Entry:
        if self.__entry is None:
            self.__entry = self.load_entry()
        return self.__entry

    def __load_database(self, db_path: PathOrStr) -> PyKeePass:
        print("Loading database...")
        password = getpass.getpass(f"Enter password to unlock {db_path}: ")
        return PyKeePass(db_path, password=password)

    def add_entry(self):
        name = self.path[-1]
        group = self.db.root_group
        for p in self.path[:-1]:
            group = self.db.add_group(group, p)
        self.db.add_entry(group, name, "", "")
        self.db.save()
        print(f"Entry {'/'.join(self.path)} created, restart the script.")
        exit(0)

    def load_entry(self) -> Entry:
        entry = typing.cast(typing.Optional[Entry], self.db.find_entries(path=self.path, first=True))
        if entry is None:
            return self.add_entry()
        return entry

    def load_attachment(self) -> bytes:
        print("Fetching attachment data...")
        attachment: list[Attachment] = self.entry.attachments
        if len(attachment) < 1:
            return b""
        return attachment[0].data

    def add_attachment(self, data: bytes):
        attachment: list[Attachment] = self.entry.attachments
        if len(attachment) > 1:
            at = attachment[0]
            self.entry.delete_attachment(at)
            self.db.delete_binary(at.id)

        binary_id = self.db.add_binary(data)
        self.entry.add_attachment(binary_id, "fish_history")
        self.db.save()


class FishManager:
    def __init__(self) -> None:
        self.fish_history_path = Path.home() / ".local/share/fish/fish_history"
        self.backup_file = Path.home() / ".local/share/fish/fish_history.bkp"

    def backup(self):
        print("Backing up fish history...")
        self.backup_file.touch()
        self.backup_file.write_text(self.fish_history_path.read_text())
    
    def read_history(self) -> str:
        print("Reading fish history...")
        return self.fish_history_path.read_text()

    def save_history(self, contents: str):
        return self.fish_history_path.write_text(contents)


def main():
    name = sys.argv[0]
    if len(sys.argv) < 3:
        print(f"Usage: python {name} path-to-kdbx path/to/credential")
        exit(1)
    db_path = sys.argv[1]
    raw_path = sys.argv[2]

    keepass = KeepassManager(db_path, raw_path)
    fish = FishManager()
    attachment_data = keepass.load_attachment().decode()
    fish_history = fish.read_history()
    print(f"Current history len: {len(fish_history)}")
    print("Merging history...")
    concat_fish_history = dedup(f"{attachment_data}\n{fish_history}")
    print(f"New fish history len: {len(concat_fish_history)}")
    fish.backup()
    print("Saving history...")
    fish.save_history(concat_fish_history)
    keepass.add_attachment(concat_fish_history.encode())
    print("Done!")


if __name__ == "__main__":
    main()

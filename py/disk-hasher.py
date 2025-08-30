import hashlib
import sys
import threading
from multiprocessing.pool import ThreadPool
from pathlib import Path
from time import sleep
from typing import Callable


def save(file: Path, content: dict[str, str]):
    text = "\n".join([f"{name}: {sha}" for name, sha in content.items()]) + "\n"
    with open(file, "a") as f:
        f.write(text)


def load(file: Path) -> dict[str, str]:
    if not file.exists():
        return {}
    with open(file, "r") as f:
        text = f.read()
        items = {}
        for line in text.splitlines():
            line = line.strip()
            if line == "":
                continue
            name, sha = line.split(": ")
            items[name] = sha
        return items


class Manager:
    root = Path()
    home = Path.home()
    __target_file_name = "disk-hashes.txt"
    target_file = root / __target_file_name
    total = 0
    current = 0
    lock = threading.Lock()
    __items: dict[str, str] = {}
    stop_event = threading.Event()

    def init(self, root: Path = Path(), callback: Callable[[], None] | None = None):
        self.root = root
        self.target_file = root / self.__target_file_name
        self.__items = load(self.target_file)
        self.progress_text = ""
        self.progress_thread = threading.Thread(target=self.progress, daemon=True)
        self.progress_thread.start()
        if callback != None:
            callback()
        manager.finish()

    def print(self, text: str, now=False):
        text = text.replace(str(self.home), "")
        self.progress_text = text
        if now:
            self.__progress(text)

    def __progress(self, text: str):
        message = f"[{self.current}/{self.total}]" + ("" if text == "" else f": {text}")
        print(" " * len(message), end="\r", flush=True)
        print(message, flush=True, end="\r")

    def progress(self):
        while not self.stop_event.is_set():
            self.__progress(self.progress_text)
            sleep(1)

    def save(self, name: str, sha: str):
        with self.lock:
            self.__items[name] = sha
            save(self.target_file, {name: sha})

    def exists(self, name: str):
        return self.__items.get(name) is not None

    def finish(self):
        self.stop_event.set()
        self.progress_thread.join()
        self.__progress(self.progress_text)


manager = Manager()


def build_files_list(root: Path) -> list[Path]:
    manager.print(f"Building files list for path {root}")
    files: list[Path] = []
    for entry in root.glob("*"):
        if entry.is_dir():
            files.extend(build_files_list(entry))
            continue
        files.append(entry)
    return files


def get_file_sha1(file: Path) -> str:
    sha1 = hashlib.sha1()
    with open(file, "rb") as f:
        data = f.read(2**20)
        while data:
            sha1.update(data)
            data = f.read(2**20)
    return sha1.hexdigest()


def hash_file(file: Path):
    manager.current += 1
    manager.print(f"Hashing file {file}")
    path = str(file.absolute())
    if manager.exists(path) or file == manager.target_file:
        return
    sha1 = get_file_sha1(file)
    manager.save(path, sha1)


def hash_files():
    files = build_files_list(manager.root)
    manager.total = len(files)
    with ThreadPool(50) as pool:
        p = pool.map_async(hash_file, files)
        p.wait()
        pool.close()
        pool.join()


def main():
    root = Path()
    if len(sys.argv) < 1:
        print("[WARN] Using current folder as root to hash files")
    else:
        root = Path(sys.argv[1])
    manager.init(root, hash_files)
    print()
    print("Done")


if __name__ == "__main__":
    main()

"""
backup files from a src to a dst

src and dst must contain a file called `disk-hashes.txt`
the file hold key: value pairs, where the key is the path of the file and the value is the hash of the file.

please, update the hashes file before running this script or may result in data loss!

usage:
    python script.py src dest
"""

import sys
import threading
from multiprocessing.pool import ThreadPool
from pathlib import Path
from time import sleep
from typing import Generator

type strOrPath = str | Path


class Manager:
    progress_text = ""
    current = 0
    total = 0
    last_msg_size = 0
    stop_event = threading.Event()
    progress_thread: threading.Thread
    lock = threading.Lock()

    def start(self, total_items: int):
        self.total = total_items
        self.progress_thread = threading.Thread(target=self.progress)
        self.progress_thread.start()

    def print(self, text: str, now=False):
        self.progress_text = text
        if now:
            self.__progress(text)

    def __progress(self, text: str):
        print(" " * self.last_msg_size, end="\r", flush=True)
        message = f"[{self.current}/{self.total}]" + ("" if text == "" else f": {text}")
        self.last_msg_size = len(message)
        print(message, flush=True, end="\r")

    def progress(self):
        while not self.stop_event.is_set():
            self.__progress(self.progress_text)
            sleep(1)

    def update(self):
        with self.lock:
            self.current += 1

    def finish(self):
        self.stop_event.set()
        self.progress_thread.join()
        self.__progress(self.progress_text)
        print()


manager = Manager()


def load_hashes_file(path: strOrPath) -> Generator[dict[str, str], None, None]:
    path = Path(path) / "disk-hashes.txt"
    if not path.exists():
        return
    with open(path, "r") as f:
        for line in f:
            key, value = line.split(": ")
            yield {key: value.strip()}


def __write_file(src: Path, target: Path):
    manager.print(f"[INFO] Copying {src} to {target}")
    with open(src, "rb") as s:
        with open(target, "ab") as t:
            data = s.read(8096)
            while data:
                t.write(data)
                data = s.read(8096)


def copy_file(src: Path, target: Path, override=False):
    if target.exists() and not override:
        return
    if not target.parent.exists():
        target.parent.mkdir(exist_ok=True, parents=True)
    if not target.exists():
        target.touch()
    __write_file(src, target)


def build_new_files_list(src: Path, dst: Path) -> list[dict[str, str]]:
    new_files: list[dict[str, str]] = []
    src_data = load_hashes_file(src)
    dst_data = load_hashes_file(dst)
    dst_hashes = [list(x.values())[0] for x in dst_data]
    for entry in src_data:
        for _, sha in entry.items():
            if sha in dst_hashes:
                continue
            new_files.append(entry)
            break
    return new_files


def build_dst_files(
    files: list[dict[str, str]], src: Path, dst: Path
) -> list[dict[str, str]]:
    dst_files = []
    for file in files:
        path = Path(list(file.keys())[0])
        hash = list(file.values())[0]
        new_path = str(path).replace(str(src), str(dst))
        dst_files.append({new_path: hash})
    return dst_files


def add_hash_to_dst(dst_path: Path, src_path: Path, hash: str):
    dst = str(dst_path)[::-1]
    src = str(src_path)[::-1]
    i = 0
    while i < len(src):
        if dst[i] != src[i]:
            break
        i += 1
    root = Path(dst[i:][::-1]) / "disk-hashes.txt"
    with open(root, "a") as f:
        f.write(f"{dst_path}: {hash}\n")


def __backup(new_files: tuple[dict[str, str], dict[str, str]]):
    src, dst = new_files
    src_path = Path(list(src.keys())[0])
    dst_path = Path(list(dst.keys())[0])
    try:
        copy_file(src_path, dst_path)
        add_hash_to_dst(dst_path, src_path, list(src.values())[0])
    except Exception as e:
        manager.print(f"Failed to copy {src_path}, err is {e}", True)
    finally:
        manager.update()


def backup(src: strOrPath, dst: strOrPath):
    src = Path(src)
    dst = Path(dst)
    if not src.exists() or not dst.exists():
        raise FileNotFoundError("src or dst folder does not exists")
    new_files = build_new_files_list(src, dst)
    dst_files = build_dst_files(new_files, src, dst)
    print(f"[INFO] Found {len(new_files)} new files")
    manager.start(len(new_files))
    with ThreadPool(20) as pool:
        pool.map_async(__backup, zip(new_files, dst_files))
        pool.close()
        pool.join()
    manager.finish()


def main():
    if len(sys.argv) < 3:
        print(f"Usage: python {sys.argv[0]} src/ dst/")
        exit(1)
    src = sys.argv[1]
    dst = sys.argv[2]
    backup(src, dst)


if __name__ == "__main__":
    main()

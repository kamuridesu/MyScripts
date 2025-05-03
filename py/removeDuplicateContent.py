import os
import hashlib
from multiprocessing.pool import Pool, ThreadPool


def getAllFoldersInsideRoot(base_path: str = "./content/") -> list[str]:
    all_dirs = []
    for path, _, _ in os.walk(base_path):
        all_dirs.append(path)
    return all_dirs


def calculateMD5(data):
    folder = data['folder']
    file = data['file']
    try:
        file_path = os.path.join(folder, file)
        if os.path.isfile(file_path):
            with open(file_path, 'rb') as f:
                _hash = hashlib.md5(f.read()).hexdigest()
                return ({
                    "hash": _hash,
                    "path": file_path
                })
    except PermissionError:
        pass
        

def getFileHashes(folder: str) -> list[dict]:
    print(f"calculating md5 for files in folder {folder}")
    data = [{"folder": folder, "file": x} for x in os.listdir(folder)]
    hashed_files = []
    with ThreadPool(30) as pool:
        results = pool.map_async(calculateMD5, data)
        if (_hash := results.get()):
            hashed_files.extend(_hash)
        pool.close()
        pool.join()
    return hashed_files


def deleteDups(file_infos: list[dict]):
    hashes = []
    first_file = {}
    for file in file_infos:
        if file is not None:
            if file['hash'] not in hashes:
                hashes.append(file['hash'])
                first_file[file['hash']] = file['path']
            else:
                print(f"Deleting {file['path']}! Equals with {first_file[file['hash']]}!")
                os.remove(file['path'])


if __name__ == "__main__":
    folders = getAllFoldersInsideRoot()
    file_infos = []
    with Pool(30) as pool:
        results = pool.map_async(getFileHashes, folders)
        if (infos := results.get()):
            for i in infos:
                file_infos.extend(i)
        pool.close()
        pool.join()
    deleteDups(file_infos)

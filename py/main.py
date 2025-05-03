import pyzipper

from pathlib import Path
from multiprocessing.pool import Pool

root = Path(".")
pwd = b"test"


def unzip(file: Path, pwd: bytes):
    print(f"Extracting {file}")
    try:
        with pyzipper.AESZipFile(file) as zf:
            zf.extractall(pwd=pwd)
        file.unlink()
    except Exception as e:
        print(f"Error extracting {file}, error is {e}")


if __name__ == "__main__":
    with Pool() as pool:
        res = pool.starmap_async(unzip, ((x, pwd) for x in root.glob("*.zip")))
        res.wait()
        pool.close()
        pool.join()
    print("Done")

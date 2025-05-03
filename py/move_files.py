"""this checks if a file is a img and moves it to the
destination folder"""


def check_if_image(PATH, elems=[], full_path=[]):
    import os

    if os.path.isdir(PATH):
        if (PATH[len(PATH) - 1] != "/"):
            PATH = PATH + "/"

        files = os.listdir(PATH)
        imageFilesExtentions = ["jpg", "png", "PNG", "JPG",
                                "jpeg", "JPEG", "ico", "ICO"]

        for file in files:
            try:
                file_extension = file.split(".")[1]
                if file_extension in imageFilesExtentions:
                    elems.append(file)
                    full_path.append(PATH + file)
            except IndexError:
                pass
            if os.path.isdir(PATH + file + "/"):
                check_if_image(PATH + file + "/")
        return full_path
    else:
        return PATH


def mv_img(origin, target):
    from subprocess import call
    if (target[len(target) - 1] != "/"):
        target = target + "/"
    if isinstance(origin, list):
        for path in origin:
            call(f'mv {path} {target}', shell=True)
    else:
        call(f'mv {origin} {target}', shell=True)


if __name__ == "__main__":
    import sys
    import os
    origin = sys.argv[1]
    try:
        target = sys.argv[2]
        if (os.path.isdir(
            origin) or os.path.isfile(
                origin)) and os.path.isdir(target):
            print("Verifiyng files...")
            mv_img(check_if_image(origin), target)
            print("Done!")
        else:
            sys.stdout.write("Error! Check if the path of the ")
            sys.stdout.write("folders are correct and try again!\n")
            sys.exit(0)
    except IndexError:
        if origin == "-h":
            sys.stdout.write("Usage: python indexingFiles.py files-path-folder")
            sys.stdout.write("path-target-folder.\n")
            sys.stdout.write("You can pass a unique image too")
        else:
            print("Ops, looks like something went wrong")

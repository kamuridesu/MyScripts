import traceback
import sys
import os
from PIL import Image
from PyPDF2 import PdfFileMerger
from PIL import ImageFile
import pathlib
ImageFile.LOAD_TRUNCATED_IMAGES = True


class folder2pdf:
    def __init__(self, path, debug=False):
        self.path = path
        self.all_var = {}  # must rename this (1)
        self.index = 0
        self.total_files = 0
        self.prog = 0  # count the number of file processed
        self.progress_x = None  # progress for the progress bar
        self.chunked = []  # chunks the files if has more than 100 images
        self.debug = debug  # this is for debug only
        self.errors = []
        self.main()

    # -- progress bar, not really necessary --#
    def percentage(self, x, y):
        """ calculates the percentage of completed pdfs"""
        return (100 * y) / x

    def startProgress(self, title):
        """ starts the progress bar"""
        print(title + ": [" + "-" * 40 + "]" + chr(8) * 41, flush=True, end="")
        self.progress_x = 0

    def progress(self, x):
        """ updates the progress bar"""
        x = int(x * 40 // 100)
        print("#" * (x - self.progress_x), flush=True, end="")
        self.progress_x = x

    def endProgress(self):
        """ ends the progress bar"""
        print("#" * (40 - self.progress_x) + "]", flush=True)
        self.progress_x = None

    def check_ext(self, filename):
        """checks the extention of the file to see if
        it's an supported image"""
        try:
            imageFilesExtentions = ["jpg", "png", "PNG", "JPG",
                                    "jpeg", "JPEG", "ico", "ICO",
                                    "WEBP", "webp"]
            file_ext = filename.split(".")
            file_ext = file_ext[len(file_ext) - 1]
            if file_ext in imageFilesExtentions:
                return True
            else:
                return False
        except Exception:
            print("\nErro! Envie o erro abaixo para @kamuridesu:")
            traceback.print_exc()
            raise SystemExit

    def chunks(self, filelist, size):
        """chunks the files as an generator to
        avoid using all the system memory"""
        n = max(1, size)
        return (filelist[i:i + n] for i in range(0, len(filelist), n))

    def merge(self, name):
        """ merges the pdfs if chunked chunked"""
        print("Unindo PDFs...")
        merger = PdfFileMerger()
        for pdf in self.chunked:
            merger.append(pdf)
        merger.write(name)
        print(sys.getsizeof(merger))
        merger.close()
        for pdf in self.chunked:
            os.remove(pdf)

    def img2pdf(self, pdfname, path, target):
        """ converts the images to pdf"""
        if not self.debug:
            self.startProgress(f"Convertendo {pdfname}")
        try:
            pdfname = os.path.join(target, pdfname) + ".pdf"

            files = os.listdir(path)
            files.sort()
            if len(files) > 100:
                chunk = self.chunks(files, 100)
            else:
                chunk = [files]
            z = 0
            for files in chunk:
                img_paths = []
                i = 0
                im1 = None
                pdf = pdfname + str(z)
                for file in files:
                    if self.check_ext(file):
                        if i == 0:
                            im1 = os.path.join(path, str(file))
                            im1 = Image.open(im1).convert("RGB")
                        else:
                            filepath = os.path.join(path, str(file))
                            img_paths.append(
                                Image.open(filepath).convert("RGB"))
                        self.prog += 1
                        if not self.debug:
                            self.progress(
                                self.percentage(self.total_files, self.prog))
                        i += 1

                if isinstance(chunk, list):
                    if im1 is not None:
                        im1.save(pdfname, "PDF", resolution=100.0,
                                 save_all=True, append_images=img_paths)
                else:
                    if im1 is not None:
                        im1.save(pdf, "PDF", resolution=100.0,
                                 save_all=True, append_images=img_paths)
                        self.chunked.append(pdf)
                z += 1
            if not self.debug:
                self.endProgress()
            if not isinstance(chunk, list):
                self.merge(name=pdfname)
        except Exception:
            print("\nErro! Envie o erro abaixo para @kamuridesu:")
            traceback.print_exc()
            raise SystemExit

    def get_all_files_in_folder(self, folder):
        try:
            listdir = os.listdir(folder)
            new_listdir = []
            files = []
            dirs = []
            for file_or_folder in listdir:
                new_listdir.append(os.path.join(folder, file_or_folder))
            for file_or_folder in new_listdir:
                if os.path.isfile(file_or_folder):
                    if self.check_ext(file_or_folder):
                        if (os.stat(file_or_folder).st_size) != 0:
                            files.append(file_or_folder)
                        else:
                            self.errors.append(str(pathlib.Path(file_or_folder).parent.absolute()))
                else:
                    dirs.append(file_or_folder)
            self.all_var[self.index] = [files, folder]
            self.index += 1
            return files, dirs
        except Exception:
            print("\nErro! Envie o erro abaixo para @kamuridesu:")
            traceback.print_exc()
            raise SystemExit

    def check_if_image(self, PATH, elems=[]):
        files = []
        results = self.get_all_files_in_folder(PATH)
        files.append(results[0])
        for directory in results[1]:
            self.check_if_image(directory, elems)
        return results

    def main(self):
        try:
            k = (self.check_if_image(self.path))
            folders = []
            images = []
            for k, v in self.all_var.items():
                folders.append(v[1])
                images.append(v[0])
            for i in images:
                self.total_files += len(i)

            i = 0
            for folder in folders:
                if folder not in self.errors:
                    filename = os.path.basename(folder)
                    lis = os.listdir(folder)
                    if len(lis) > 0:
                        self.img2pdf(pdfname=filename, path=folder,
                                     target=folders[0])
                        self.chunked = []
                    i += 1
            print("Finalizado com sucesso!")
            if len(self.errors) > 0:
                print("Não foi possível converter as seguintes pastas:")
                for fol in self.errors:
                    print(fol)
        except Exception:
            print("\nErro! Envie o erro abaixo para @kamuridesu:")
            traceback.print_exc()
            raise SystemExit


if __name__ == "__main__":
    debug = False
    if debug:
        path = os.path.join(
            str(pathlib.Path(__file__).parent.absolute()), "mango")
    else:
        path = input(
            "Insira o caminho da pasta onde estão os arquivos para transformar em PDF: ")
    if not os.path.isdir(path):
        print("Erro! Verifique se o caminho inserido é uma pasta!")
        raise SystemExit
    else:
        folder2pdf(path, debug)

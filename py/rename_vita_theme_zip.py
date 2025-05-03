import os
import glob
import zipfile

from bs4 import BeautifulSoup


def read_xml(filename):
    archive = zipfile.ZipFile(filename)
    xml = archive.read("theme.xml")
    archive.close()
    return xml


def get_project_name(xml_content):
    soup: BeautifulSoup = BeautifulSoup(xml_content, "xml")
    results = soup.findAll("m_title")
    for result in results:
        return result.find("m_default").text


if __name__ == "__main__":
    for file in glob.glob("./*.zip"):
        xml = read_xml(file)
        title = get_project_name(xml)
        os.rename(file, f"{title}.zip")

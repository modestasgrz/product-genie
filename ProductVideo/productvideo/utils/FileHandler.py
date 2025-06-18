import base64
import os
from zipfile import ZipFile
import numpy as np
import json
import io
from pathlib import Path
try:
    to_unicode = unicode
except NameError:
    to_unicode = str


def extractZipFile(filepath, directory):
    with ZipFile(filepath, 'r') as zip:
        # zip.printdir()
        zip.extractall(directory)


def compressZipFile(filepath, directory):

    # calling function to get all file paths in the directory
    file_paths = get_all_file_paths(directory)

    # printing the list of all files to be zipped
    # print('Following files will be zipped:')
    # for file_name in file_paths:
    #     print(file_name)

    # writing files to a zipfile
    with ZipFile(filepath, 'w') as zip:
        # writing each file one by one
        for file in file_paths:
            zip.write(file, os.path.basename(file))


def saveZipFile(filename, data):
    with open(filename, "wb") as fh:
        fh.write(base64.b64decode(data))


def loadZipFile(filename):
    with open(filename, "rb") as fh:
        out_data = base64.b64encode(fh.read())

    return out_data


def get_all_file_paths(directory):

    # initializing empty file paths list
    file_paths = []

    # crawling through directory and subdirectories
    for root, directories, files in os.walk(directory):
        for filename in files:
            # join the two strings in order to form the full filepath.
            filepath = os.path.join(root, filename)
            file_paths.append(filepath)

    # returning all file paths
    return file_paths


def readBinaryFile(file_name):
    data = np.fromfile(file_name, dtype='uint8')
    return data


def writeBinaryFile(file_name, data):

    if not os.path.exists(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name))

    return data.astype('uint8').tofile(file_name)


def readCSV(file_name):
    return np.genfromtxt(file_name, delimiter=',', dtype=int)


def writeCSV(file_name, data, size=None):
    if not os.path.exists(os.path.dirname(file_name)):
        os.makedirs(os.path.dirname(file_name))
    if size is not None:
        data = data.reshape(size)
    return np.savetxt(file_name, data.astype(int), fmt='%i', delimiter=",")


def getTickers(file_name):
    data = json.loads(open(file_name))
    return data


def writeJsonData(filename, data):
    # Write JSON file
    with io.open(filename, 'w', encoding='utf8') as outfile:
        str_ = json.dumps(data,
                          indent=4,
                          sort_keys=True,
                          separators=(',', ': '),
                          ensure_ascii=False)
        outfile.write(to_unicode(str_))


def getFilesWithExtensions(dir_path, types):
    files = [str(p) for p in Path(dir_path).glob("**/*") if p.suffix in types]
    return files


def readJsonData(filename):
    # Read JSON file
    with open(filename, encoding='utf8') as data_file:
        data_loaded = json.load(data_file)
    return data_loaded

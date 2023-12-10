import hashlib
import os

def get_file_hash(file_src=None, file_paths=None):
    if file_src:
        file_paths = [x.name for x in file_src]
    file_paths.sort(key=lambda x: os.path.basename(x))

    md5_hash = hashlib.md5()
    for file_path in file_paths:
        with open(file_path, "rb") as f:
            while chunk := f.read(8192):
                md5_hash.update(chunk)

    return md5_hash.hexdigest()

def get_all_files_in_directory(path):
    all_files = []

    for root, dirs, files in os.walk(path):
        for file in files:
            file_path = os.path.join(root, file)
            all_files.append(os.path.abspath(file_path))

    return all_files
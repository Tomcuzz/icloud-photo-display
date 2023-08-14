"""Path functions"""
import os


def clean_filename(filename):
    """Replaces invalid chars in filenames with '_'"""
    result = filename.encode(
        "utf-8").decode("ascii", "ignore")
    invalid = '<>:"/\\|?*\0'

    for char in invalid:
        result = result.replace(char, '_')

    return result


def local_download_path(media, size, download_dir):
    """Returns the full download path, including size"""
    filename = filename_with_size(media, size)
    download_path = os.path.join(download_dir, filename)
    return download_path


def filename_with_size(media, size):
    """Returns the filename with size, e.g. 12345-IMG1234.jpg, 45678-IMG1234.jpg"""
    # Strip any non-ascii characters.
    filename = clean_filename(media.filename)
    return str(size) + "-" + filename

def get_files_on_disk(photo_dir):
    to_return = {}
    for disk_file_name in os.listdir(photo_dir):
        file_name_components = disk_file_name.split("-")
        filename = disk_file_name
        file_path = photo_dir + '/' + disk_file_name
        if len(file_name_components) > 1: 
            filename = "-".join(file_name_components[1:])
        to_return[filename] = {
            'size': file_name_components[0],
            'disk_file_name': disk_file_name,
            'file_path': file_path,
            'file_name': filename
        }
    return to_return
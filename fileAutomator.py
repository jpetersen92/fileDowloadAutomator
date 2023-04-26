import zipfile
import shutil as s
import os

from os import scandir, rename, remove, walk, mkdir
from os.path import splitext, exists, join, isdir
from shutil import move
from time import sleep

import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# ? folder to track e.g. Windows: "C:\\Users\\UserName\\Downloads"
source_dir = "/Users/jospeter3/Downloads"
dest_dir_sfx = "/Users/jospeter3/Desktop/audio"
dest_dir_music = "/Users/jospeter3/Desktop/audio"
dest_dir_video = "/Users/jospeter3/Desktop/video"
dest_dir_image = "/Users/jospeter3/Desktop/images"
dest_dir_documents = "/Users/jospeter3/Desktop/documents"
dest_dir_dev = "/Users/jospeter3/Desktop/dev"
dest_dir_staging = "/Users/jospeter3/Documents/staging"

# ? supported image types
image_extensions = [".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi", ".png", ".gif", ".webp", ".tiff", ".tif", ".psd", ".raw", ".arw", ".cr2", ".nrw", ".k25", ".bmp", ".dib", ".heif", ".heic", ".ind", ".indd", ".indt", ".jp2", ".j2k", ".jpf", ".jpf", ".jpx", ".jpm", ".mj2", ".svg", ".svgz", ".ai", ".eps", ".ico"]
# ? supported Video types
video_extensions = [".webm", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".ogg",
                    ".mp4", ".mp4v", ".m4v", ".avi", ".wmv", ".mov", ".qt", ".flv", ".swf", ".avchd"]
# ? supported Audio types
audio_extensions = [".m4a", ".flac", "mp3", ".wav", ".wma", ".aac"]
# ? supported Document types
document_extensions = [".doc", ".docx", ".odt", ".pdf", ".xls", ".xlsx", ".ppt", ".pptx", ".csv"]
# ? supported Dev types
dev_extensions = [".html", ".js", ".css", ".scss", ".md", ".json", ".py"]


def make_unique(dest, name):
    filename, extension = splitext(name)
    counter = 1
    # * IF FILE EXISTS, ADDS NUMBER TO THE END OF THE FILENAME
    while exists(f"{dest}/{name}"):
        name = f"{filename}({str(counter)}){extension}"
        counter += 1

    return name


def move_file(dest, entry, name):
    filename = os.path.basename(name)
    if exists(f"{dest}/{filename}"):
        unique_name = make_unique(dest, filename)
        oldName = join(dest, filename)
        newName = join(dest, unique_name)
        rename(oldName, newName)
    move(entry, dest)


class MoverHandler(FileSystemEventHandler):
    # ? THIS FUNCTION WILL RUN WHENEVER THERE IS A CHANGE IN "source_dir"
    # ? .upper is for not missing out on files with uppercase extensions

    def on_modified(self, event):
        with scandir(source_dir) as entries:
            for entry in entries:
                name = entry.name
                if name.endswith('.zip'): # If the entry is a .zip file
                    self.extract_file_from_zip(entry.path)
                else:
                    self.check_audio_files(entry, name)
                    self.check_video_files(entry, name)
                    self.check_image_files(entry, name)
                    self.check_document_files(entry, name)
                    self.check_dev_files(entry, name)



    def extract_file_from_zip(self, zip_path):
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for filename in zip_ref.namelist():
                if not filename.endswith('/'): # skip directories
                    file_extension = os.path.splitext(filename)[1].lower()
                    if file_extension in audio_extensions:
                        dest = dest_dir_sfx if zip_ref.getinfo(filename).file_size < 10_000_000 else dest_dir_music
                        extracted_file_path = zip_ref.extract(filename, dest_dir_staging)
                        move_file(dest, extracted_file_path, filename)
                        logging.info(f"Extracted and moved audio file: {filename}")
                        remove(zip_path)
                    elif file_extension in video_extensions:
                        extracted_file_path = zip_ref.extract(filename, dest_dir_staging)
                        move_file(dest_dir_video, extracted_file_path, filename)
                        logging.info(f"Extracted and moved video file: {filename}")
                        remove(zip_path)
                    elif file_extension in image_extensions:
                        extracted_file_path = zip_ref.extract(filename, dest_dir_staging)
                        move_file(dest_dir_image, extracted_file_path, filename)
                        logging.info(f"Extracted and moved image file: {filename}")
                        remove(zip_path)
                    elif file_extension in document_extensions:
                        extracted_file_path = zip_ref.extract(filename, dest_dir_staging)
                        move_file(dest_dir_documents, extracted_file_path, filename)
                        logging.info(f"Extracted and moved document file: {filename}")
                        remove(zip_path)


        
    def check_audio_files(self, entry, name):  # * Checks all Audio Files
        for audio_extension in audio_extensions:
            if name.endswith(audio_extension) or name.endswith(audio_extension.upper()):
                if entry.stat().st_size < 10_000_000 or "SFX" in name:  # ? 10Megabytes
                    dest = dest_dir_sfx
                else:
                    dest = dest_dir_music
                move_file(dest, entry, name)
                logging.info(f"Moved audio file: {name}")

    def check_video_files(self, entry, name):  # * Checks all Video Files
        for video_extension in video_extensions:
            if name.endswith(video_extension) or name.endswith(video_extension.upper()):
                move_file(dest_dir_video, entry, name)
                logging.info(f"Moved video file: {name}")

    def check_image_files(self, entry, name):  # * Checks all Image Files
        for image_extension in image_extensions:
            if name.endswith(image_extension) or name.endswith(image_extension.upper()):
                move_file(dest_dir_image, entry, name)
                logging.info(f"Moved image file: {name}")

    def check_document_files(self, entry, name):  # * Checks all Document Files
        for documents_extension in document_extensions:
            if name.endswith(documents_extension) or name.endswith(documents_extension.upper()):
                move_file(dest_dir_documents, entry, name)
                logging.info(f"Moved document file: {name}")
    def check_dev_files(self, entry, name):  # * Checks all Document Files
        for dev_extension in dev_extensions:
            if name.endswith(dev_extension) or name.endswith(dev_extension.upper()):
                move_file(dest_dir_dev, entry, name)
                logging.info(f"Moved dev file: {name}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = source_dir
    event_handler = MoverHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(10)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()

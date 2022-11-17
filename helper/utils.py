import os
import gdown
import zipfile
import helper.const as constant


def google_drive_downloader(url, output):
    gdown.download(url, output, quiet=True)


def download_resource():
    # Checking and download resource
    if not os.path.exists(constant.lipsync_directory):
        if not os.path.exists(constant.lipsync_directory):
            google_drive_downloader(constant.lipsync_controller_download_path, constant.lipsync_zip)
        with zipfile.ZipFile(constant.lipsync_zip, "r") as zip_ref:
            zip_ref.extractall('.')

    if not os.path.exists(constant.tts_directory):
        if not os.path.exists(constant.tts_directory):
            google_drive_downloader(constant.tts_download_path, constant.tts_zip)
        with zipfile.ZipFile(constant.tts_zip, "r") as zip_ref:
            zip_ref.extractall('.')
            os.rename('lipsync', 'res')


if __name__ == '__main__':
    download_resource()

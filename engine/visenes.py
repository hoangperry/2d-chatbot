import os
import json
import subprocess
import numpy as np


DATA_FRAME_RATE = 30
# pocketSphinx is a open source for English recordings, `phonetic` use for non-English recordings
RECOGNIZER_LIST = ['pocketSphinx', 'phonetic']
LANGUAGE = 'en'

# GHX for use all G H and X Shape
EXTEND_SHAPE = "GHX"

# output format support .TSV, .XML, .JSON, .DAT
OUTPUT_FORMAT = 'json'


if LANGUAGE == 'en':
    RECOGNIZER = RECOGNIZER_LIST[0]
else:
    RECOGNIZER = RECOGNIZER_LIST[1]


def generate_cli(audio_path, dialog_path):
    visemes_gen_command = ['./controller', audio_path]
    # Get return code and run quite
    visemes_gen_command += ['--machineReadable', '--quiet']
    # Set recognizer
    visemes_gen_command += ['-r', RECOGNIZER]
    # Set Extended shape
    visemes_gen_command += ['--extendedShapes', EXTEND_SHAPE]
    # set dialog file
    if dialog_path is not None:
        visemes_gen_command += ['-d', dialog_path]
    # Set data frame rate
    visemes_gen_command += ['--datFrameRate', DATA_FRAME_RATE]
    # Assign output format
    visemes_gen_command += ['-f', OUTPUT_FORMAT]

    return visemes_gen_command


def predict_visemes_from_file(audio_path, dialog_path):
    command_response = subprocess.run(
        generate_cli(audio_path, dialog_path),
        capture_output=True,
        text=True
    )
    return command_response.stdout, True if command_response.returncode == 0 else False


if __name__ == '__main__':
    input_audio = 'alo123.wav'
    dialog_txt = 'dialog.txt'
    result = predict_visemes_from_file(input_audio, dialog_txt)
    print(result)
    visemes = json.loads(result.stdout)
    print(visemes)


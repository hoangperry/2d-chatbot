import os
import io
import json
import shutil
import base64
import numpy as np

from scipy.io.wavfile import write

from helper.utils import ensure_dir, id_generator
from engine.visenes import predict_visemes_from_file

from vietTTS import nat_normalize_text
from vietTTS.nat.text2mel import text2mel
from vietTTS.hifigan.mel2wave import mel2wave


# Text2Mel config
LEXICON_FILE = "tts/lexicon.txt"
SILENCE_DURATION = 0.2
ACOUSTIC_MODEL = "tts/acoustic_latest_ckpt.pickle"
DURATION_MODEL = "tts/duration_latest_ckpt.pickle"

MEL_CONFIG_FILE = "tts/config.json"
MEL_MODEL = "tts/hk_hifi.pickle"
SAMPLE_RATE = 16_000


def text_to_speech(text: str) -> np.ndarray:
    # if len(text) > 500:
    #     text = text
    text = nat_normalize_text(text)
    mel = text2mel(text, LEXICON_FILE, SILENCE_DURATION, ACOUSTIC_MODEL, DURATION_MODEL)
    wave = mel2wave(mel, MEL_CONFIG_FILE, MEL_MODEL)
    return (wave * (2 ** 15)).astype(np.int16)


def write_wav(output_file, audio_array, sample_rate=None):
    # # """numpy array to WAV"""
    # channels = 2 if (audio_array.ndim == 2 and audio_array.shape[1] == 2) else 1
    # # normalized array - each item should be a float in [-1, 1)
    # if normalized:
    #     y = np.int16(audio_array * 2 ** 15)
    # else:
    #     y = np.int16(audio_array)
    # song = pydub.AudioSegment(y.tobytes(), frame_rate=sample_rate, sample_width=2, channels=channels)
    # song.export(output_file, format="wav", bitrate="320k")
    ensure_dir(os.path.dirname(output_file))
    sample_rate = SAMPLE_RATE if sample_rate is None else sample_rate
    scaled = np.int16(audio_array / np.max(np.abs(audio_array)) * 32767)
    write(output_file, sample_rate, scaled)


def generate_audio_and_visemes(text: str) -> (np.ndarray, dict):
    np_audio = text_to_speech(text)
    tmp_directory = 'tmp/' + id_generator(True)
    audio_file = f'{tmp_directory}/tts-audio.wav'
    text_file = f'{tmp_directory}/dialog.txt'
    write_wav(audio_file, np_audio)

    # Create dialog file
    with open(text_file, mode='w', encoding='utf-8') as tmp_file:
        tmp_file.write(text)

    visemes, success = predict_visemes_from_file(audio_file, text_file)
    # Clear temporary file
    shutil.rmtree(tmp_directory)

    if not success:
        return np_audio, None
    return np_audio, json.loads(visemes)


def np_to_base64(audio):
    byte_io_file = io.BytesIO()
    write(byte_io_file, SAMPLE_RATE, audio)
    img_byte = byte_io_file.getvalue()
    return base64.b64encode(img_byte).decode()


if __name__ == '__main__':
    input_text = 'Chào các bạn hihi'
    # print(type(text_to_speech('123')))
    # write_wav('123123123/alo123.wav', text_to_speech(input_text))
    # with open('dialog.txt', mode='w', encoding='utf-8') as ff:
    #     ff.write(input_text)

    new_audio = text_to_speech(input_text)
    print(np_to_base64(new_audio))

import os
import cv2
import time
import json
import glob
import pydub
import shutil

import numpy as np

from vietTTS.hifigan.mel2wave import mel2wave
from vietTTS.nat.text2mel import text2mel
from vietTTS import nat_normalize_text

from shlex import quote as shlex_quote


class Artist:
    def __init__(self, fps=None, character=None):
        self.fps = fps if fps is not None else 24
        self.character = character if character is not None else 'morty'

    @staticmethod
    def text_to_speech(text):
        # if len(text) > 500:
        #     text = text
        text = nat_normalize_text(text)
        mel = text2mel(
            text,
            "tts/lexicon.txt",
            0.2,
            "tts/acoustic_latest_ckpt.pickle",
            "tts/duration_latest_ckpt.pickle",
        )
        wave = mel2wave(mel, "tts/config.json", "tts/hk_hifi.pickle")
        return (wave * (2 ** 15)).astype(np.int16)

    @staticmethod
    def write(f, sr, x, normalized=False):
        """numpy array to MP3"""
        channels = 2 if (x.ndim == 2 and x.shape[1] == 2) else 1
        if normalized:  # normalized array - each item should be a float in [-1, 1)
            y = np.int16(x * 2 ** 15)
        else:
            y = np.int16(x)
        song = pydub.AudioSegment(y.tobytes(), frame_rate=sr, sample_width=2, channels=channels)
        song.export(f, format="wav", bitrate="320k")

    def text_to_animation(self, text, output_file=None, write_video=True, clear_tmp=True):
        tmp_dir = 'tmp/' + str(time.time()).replace('.', '_')
        if not os.path.exists(tmp_dir):
            os.makedirs(tmp_dir)

        input_audio = f'{tmp_dir}/tts.wav'
        self.write(input_audio, sr=16_000, x=self.text_to_speech(text))
        rhubard_command = f'./controller {input_audio} -r phonetic --datFrameRate 60 -f json -o {tmp_dir}/shape.json'
        os.system(rhubard_command)
        data = json.load(open(f"{tmp_dir}/shape.json"))
        data = [[i['end'], i['value']] for i in data['mouthCues']]

        character_pose = dict()
        size = None

        for i in glob.glob(f'character/{self.character}/*.png'):
            character_img = cv2.imread(i)
            character_pose[i.split('/')[-1].split('.')[0]] = character_img
            height, width, layers = character_img.shape
            size = (width, height)

        if size is None:
            raise Exception('Not found Character')

        tmp_mp4 = f'{tmp_dir}/project.mp4'
        out = cv2.VideoWriter(tmp_mp4, cv2.VideoWriter_fourcc(*'mp4v'), self.fps, size)
        frame_time = 1 / self.fps
        current_time = 0

        for i in data:
            while True:
                if current_time > float(i[0]):
                    break
                else:
                    out.write(character_pose[i[1].lower()])
                    current_time += frame_time
        out.release()
        if write_video:
            output_file = output_file if output_file is not None else self.character + '_' \
                                                                      + str(time.time()).replace('.', '_')
            cmd_ffmpeg = f'ffmpeg -i {tmp_mp4} -i {input_audio} -map 0 -map 1:a -c:v copy -shortest {output_file}.mp4'
            os.system(cmd_ffmpeg)
        if clear_tmp:
            shutil.rmtree(tmp_dir)
        return tmp_mp4, input_audio, tmp_dir

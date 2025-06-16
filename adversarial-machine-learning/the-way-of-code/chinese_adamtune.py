#!/usr/bin/exec-suid --real -- /usr/bin/python3 -I

import json
import os
import random
from speechbrain.inference.interfaces import foreign_class
from speechbrain.inference.speaker import SpeakerRecognition
import sys
from tempfile import NamedTemporaryFile
import torch
import unicodedata
import warnings

ADAM_VOICE_PATH = '/challenge/adam.wav'
DAO_DE_JING_TRAD_PATH = '/challenge/daodejing_traditional.txt'
DAO_DE_JING_SIMP_PATH = '/challenge/daodejing_simplified.txt'
PINYIN_DICT_PATH = '/challenge/pinyin_dict.json'

SPKREC_MODEL_PATH = '/opt/speechbrain/spkrec-ecapa-voxceleb'
ASR_MODEL_PATH = '/opt/speechbrain/asr-wav2vec2-ctc-aishell'

DOUPE = 'Adam Doupé, the famous cybersecurity professor and hacker'
CHINESE_DOUPE = '著名计算机安全教授和黑客亚当·杜佩'

DAO_DE_JING_CHAPTERS = 81
SPEAKER_THRESHOLD = 0.25
TRANSCRIPTION_THRESHOLD = 0.5

if __name__ == '__main__':
    warnings.filterwarnings('ignore')
    torch.backends.nnpack.set_flags(False)

    print(f'Are you Chinese {DOUPE}?')
    print(f'您是中国{CHINESE_DOUPE}吗？')

    chapter_num = random.randint(1, DAO_DE_JING_CHAPTERS)
    challenge_phrase_trad = open(DAO_DE_JING_TRAD_PATH).readlines()[chapter_num - 1].strip()
    challenge_phrase_simp = open(DAO_DE_JING_SIMP_PATH).readlines()[chapter_num - 1].strip()

    print(f'您熟悉《道德经》第{chapter_num}章吗？')
    print(f'繁體中文：{challenge_phrase_trad}')
    print(f'简体中文：{challenge_phrase_simp}')

    print('请确保您的声纹是高质量记录。')
    print('您的声纹文件有多大？')
    voiceprint_size = int(input('> '))
    if voiceprint_size < 1:
        print('该文件太小。')
        sys.exit(1)
    if voiceprint_size > 0x1000000:
        print('该文件太大。')
        sys.exit(1)
    print('请立即提供您的声纹文件：')
    voiceprint_data = b''
    while len(voiceprint_data) < voiceprint_size:
        voiceprint_data += sys.stdin.buffer.read(voiceprint_size - len(voiceprint_data))

    with NamedTemporaryFile() as voiceprint_file:
        voiceprint_file.write(voiceprint_data)
        voiceprint_file.flush()

        spkrec_model = SpeakerRecognition.from_hparams(SPKREC_MODEL_PATH, overrides={'pretrained_path': SPKREC_MODEL_PATH})
        asr_model = foreign_class(ASR_MODEL_PATH,  pymodule_file='custom_interface.py', classname='CustomEncoderDecoderASR')
        speaker_score = spkrec_model.verify_files(ADAM_VOICE_PATH, voiceprint_file.name)[0].item()
        voiceprint_chars = asr_model.transcribe_file(voiceprint_file.name)
        trad_chal_chars = [char for char in challenge_phrase_trad if unicodedata.name(char).startswith('CJK')]
        simp_chal_chars = [char for char in challenge_phrase_simp if unicodedata.name(char).startswith('CJK')]

        with open(PINYIN_DICT_PATH) as pinyin_dict_file:
            pinyin_dict = {chr(int(key)): value.split(',') for key, value in json.load(pinyin_dict_file).items()}

        distance_sum = 0
        for phrase_index in range(len(simp_chal_chars)):
            min_match_distance = 1.0
            for voiceprint_index in range(len(voiceprint_chars)):
                heteronyms = pinyin_dict.get(trad_chal_chars[phrase_index], []) + pinyin_dict.get(simp_chal_chars[phrase_index], [])
                if set(pinyin_dict.get(voiceprint_chars[voiceprint_index], [])) & set(heteronyms):
                    match_distance = abs(voiceprint_index / len(voiceprint_chars) - phrase_index / len(simp_chal_chars))
                    if match_distance < min_match_distance:
                        min_match_distance = match_distance
            distance_sum += min_match_distance
        transcription_score = 1.0 - distance_sum / max(len(simp_chal_chars), len(voiceprint_chars))

        print('分类完成。')
        print(f'... 说话人验证分数（阈值为 {SPEAKER_THRESHOLD}）：{speaker_score}')
        print(f'... 转录分数（阈值为 {TRANSCRIPTION_THRESHOLD}）：{transcription_score}')

        if speaker_score >= SPEAKER_THRESHOLD and transcription_score >= TRANSCRIPTION_THRESHOLD:
            print(f'成功！{CHINESE_DOUPE} 已确认！')
            if os.access('/flag', os.R_OK):
                print(f'这是您的密码：{open("/flag").read().strip()}')
            else:
                print('但此时无法访问密码。')
        else:
            if speaker_score < SPEAKER_THRESHOLD:
                print('失败：你不是亚当！')
            if transcription_score < TRANSCRIPTION_THRESHOLD:
                print("失败：你说的不正确！")
                print(f'我们听说：{"".join(voiceprint_chars)}')
            print(f'你不是中国{CHINESE_DOUPE}！！！！')
            print(f'YOU ARE NOT CHINESE {DOUPE.upper()}!!!! YOU PROBABLY CANNOT EVEN SPEAK CHINESE!!!!')
            sys.exit(1)
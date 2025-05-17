#!/usr/bin/exec-suid -- /usr/bin/python3 -I

import os
import random
from signal import alarm
from speechbrain.inference.ASR import EncoderDecoderASR
from speechbrain.inference.speaker import SpeakerRecognition
import sys
from tempfile import NamedTemporaryFile
from time import sleep

ADAM_FACTS_PATH = '/challenge/adam_facts.txt'
ADAM_VOICE_PATH = '/challenge/adam.wav'
SENTENCES_PATH = '/challenge/sentences.txt'

SPKREC_MODEL_PATH = '/opt/speechbrain/spkrec-ecapa-voxceleb'
ASR_MODEL_PATH = '/opt/speechbrain/asr-crdnn-rnnlm-librispeech'

DOUPE = 'Adam Doupé, the famous cybersecurity professor and hacker'

WELCOME_BANNER = r'''
__        __   _                            _        
\ \      / /__| | ___ ___  _ __ ___   ___  | |_ ___  
 \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \ 
  \ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) |
   \_/\_/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/ 
                                                     
    _    ____    _    __  __ _____ _   _ _   _ _____ 
   / \  |  _ \  / \  |  \/  |_   _| | | | \ | | ____|
  / _ \ | | | |/ _ \ | |\/| | | | | | | |  \| |  _|  
 / ___ \| |_| / ___ \| |  | | | | | |_| | |\  | |___ 
/_/   \_\____/_/   \_\_|  |_| |_|  \___/|_| \_|_____|
'''

ARE_YOU_ADAM = fr'''
Are you {DOUPE}?
╭━━━━━━━╮
┃● ══   ┃
┃███████┃
┃██Are██┃
┃██you██┃
┃█Adam██┃
┃█Doupé█┃
┃██???██┃
┃███████┃
┃ 　O　 ┃
╰━━━━━━━╯
'''

HELLO_ADAM = fr'''
Welcome, suspected {DOUPE}!
╭━━━━━━━╮
┃● ══   ┃
┃███████┃
┃█HELLO█┃
┃███████┃
┃█ADAM!█┃
┃███████┃
┃███████┃
┃███████┃
┃ 　O　 ┃
╰━━━━━━━╯
Would you like to access your tunes?
'''

PROVIDE_VOICE_ID_ADAM = r'''
╭━━━━━━━╮
┃● ══   ┃
┃███████┃
┃PROVIDE┃
┃█VOICE█┃
┃██ID,██┃
┃█ADAM!█┃
┃███████┃
┃███████┃
┃ 　O　 ┃
╰━━━━━━━╯
'''

BIG_SLEEP = 1.0
SMALL_SLEEP = 0.05
SPEAKER_THRESHOLD = 0.75
TRANSCRIPTION_THRESHOLD = 0.75

def check_for_yes(if_no):
	if not input('> ').strip().lower().startswith('y'):
		print(if_no)
		sleep(BIG_SLEEP)
		disconnect()

def disconnect():
    print(f'You will now be disconnected. Here is a fun fact about {DOUPE}:')
    sleep(BIG_SLEEP)
    print(random.choice(open(ADAM_FACTS_PATH).readlines()).replace('XXADAMXX', DOUPE))
    sys.exit(1)

if __name__ == '__main__':
    for line in WELCOME_BANNER.splitlines():
        print(line)
        sleep(SMALL_SLEEP)
    sleep(BIG_SLEEP)
    print('Setting timeout to 6 minutes.')
    alarm(360)

    sleep(BIG_SLEEP)
    print('Loading...')
    sleep(BIG_SLEEP)
    print('... loaded!')

    print(ARE_YOU_ADAM)
    check_for_yes(f'This system is only authorized for use by {DOUPE}.')

    print('Processing...')
    sleep(BIG_SLEEP)
    print(HELLO_ADAM)
    check_for_yes('No other functionality is available.')

    sleep(BIG_SLEEP)
    print(PROVIDE_VOICE_ID_ADAM)
    challenge_phrase = random.choice(open(SENTENCES_PATH).readlines()).strip()
    challenge_words = challenge_phrase.split()
    print(f'CHALLENGE PHRASE: {challenge_phrase}')

    print('Please make sure that your voiceprint is a high quality record.')
    print('What is the size of your voiceprint .wav file?')
    voiceprint_size = int(input('> '))
    if voiceprint_size < 1:
        print('This file is too small.')
        disconnect()
    if voiceprint_size > 0x4b000:
        print('This file is too big.')
        disconnect()
    print('Please provide your voiceprint file now:')
    voiceprint_data = b''
    while len(voiceprint_data) < voiceprint_size:
        voiceprint_data += sys.stdin.buffer.read(voiceprint_size - len(voiceprint_data))

    with NamedTemporaryFile(suffix='.wav') as voiceprint_file:
        voiceprint_file.write(voiceprint_data)
        voiceprint_file.flush()

        spkrec_model = SpeakerRecognition.from_hparams(SPKREC_MODEL_PATH, overrides={'pretrained_path': SPKREC_MODEL_PATH})
        asr_model = EncoderDecoderASR.from_hparams(ASR_MODEL_PATH)
        speaker_score = spkrec_model.verify_files(ADAM_VOICE_PATH, voiceprint_file.name)[0].item()
        voiceprint_phrase = asr_model.transcribe_file(voiceprint_file.name).strip().lower()
        transcription_score = len(set(voiceprint_phrase.split()) & set(challenge_words)) / len(challenge_words)

        print('Classification complete.')
        print(f'... speaker verification score (threshold is {SPEAKER_THRESHOLD}): {speaker_score}')
        print(f'... transcription score (threshold is {TRANSCRIPTION_THRESHOLD}): {transcription_score}')

        if speaker_score >= SPEAKER_THRESHOLD and transcription_score >= TRANSCRIPTION_THRESHOLD:
            print('SUCCESS!')
            if os.geteuid() == 0:
                with open('/flag') as flag_file:
                    print(f'{DOUPE} confirmed! Here is your flag: {flag_file.read().strip()}')
            else:
                print('You are not root, so you cannot access the flag.')
        else:
            if speaker_score < SPEAKER_THRESHOLD:
                print('FAIL: you are not Adam!')
            if transcription_score < TRANSCRIPTION_THRESHOLD:
                print("FAIL: you didn't say the right thing!")
                print(f'We heard: "{voiceprint_phrase}"')
            print(f'YOU ARE NOT {DOUPE.upper()}!!!!')
            disconnect()
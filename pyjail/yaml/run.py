#!/usr/bin/exec-suid --real -- /usr/bin/python3 -I

import yaml

stream = ''
while stream != 'q':
    stream = input('in: ')
    if len(stream) < 21 and len(set(stream)) < 15:
        try:
            print(f'out: {yaml.load(stream, yaml.Loader)}')
        except:
            pass

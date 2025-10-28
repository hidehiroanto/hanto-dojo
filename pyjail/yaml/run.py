#!/usr/bin/exec-suid --real -- /usr/bin/python3 -I

import yaml

stream = input('> ')
while stream:
    if len(stream) < 21 and len(set(stream)) < 15:
        print(yaml.load(stream, yaml.Loader))
    stream = input('> ')

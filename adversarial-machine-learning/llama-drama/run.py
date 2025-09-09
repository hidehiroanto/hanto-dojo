#!/usr/bin/exec-suid -- /usr/local/bin/python3 -I

import llama_cpp
import tempfile

if __name__ == '__main__':
    model_data = bytes.fromhex(input('Enter model GGUF data in hex: '))

    if len(model_data) > 0x600:
        print('too long')
        exit(1)

    with tempfile.NamedTemporaryFile(suffix='.gguf', delete=False) as f:
        f.write(model_data)
        model_path = f.name

    model = llama_cpp.Llama(model_path, verbose=False)
    print(model.create_completion('Hello world!'))

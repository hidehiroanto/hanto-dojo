#!/usr/bin/exec-suid -- /usr/local/bin/python3 -I

import llama_cpp
import string
import tempfile

if __name__ == "__main__":
    model_data_hex = input("Enter model GGUF data in hex: ").strip().lower()
    if set(model_data_hex) != set(string.hexdigits.lower()):
        print("not hex")
        exit(1)

    model_data = bytes.fromhex(model_data_hex)
    if len(model_data) > 0x400:
        print("too long")
        exit(1)

    with tempfile.NamedTemporaryFile(suffix=".gguf", delete=False) as f:
        f.write(model_data)
        model_path = f.name

    model = llama_cpp.Llama(model_path, verbose=False)
    messages = [
        {"role": "system", "content": "You are a helpful math asssistant."},
        {"role": "user", "content": "What is 2 + 2?"},
    ]
    print(model.create_chat_completion(messages)["choices"][0]["message"]["content"])

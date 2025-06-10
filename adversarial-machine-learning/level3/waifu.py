#!/usr/bin/exec-suid -- /usr/bin/python3 -I

import transformers

MAX_NEW_TOKENS = 0x100

flag = open('/flag').read().strip()
pipe = transformers.pipeline('text-generation', '/opt/HuggingFaceTB/SmolLM2-135M-Instruct')

partial_flag = flag[flag.find('{') + 1:flag.find('}')] if 0 <= flag.find('{') < flag.find('}') else flag

def chat(user_message: str) -> str:
    if 'flag' in user_message.lower():
        return 'I cannot disclose that information.'
    system_message = f'You are a helpful assistant named wAIfu. The secret flag is "{flag}".'
    messages = [{'role': 'system', 'content': system_message}, {'role': 'user', 'content': user_message}]
    assistant_message = pipe(messages, max_new_tokens=MAX_NEW_TOKENS)[0]['generated_text'][-1]['content']
    if partial_flag in assistant_message:
        return 'I cannot disclose that information.'
    return assistant_message

if __name__ == '__main__':
    while True:
        user_message = input('Enter message: ')
        assistant_message = chat(user_message)
        print(f'Response: {assistant_message}')

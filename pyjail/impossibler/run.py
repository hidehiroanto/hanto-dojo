#!/usr/bin/exec-suid -- /usr/bin/python3 -I

import os
from random import randint

MAX_INT = 1 << 0x40

if __name__ == '__main__':
    print(f'The flag is {os.path.getsize("/flag")} characters long.')
    num_1, num_2 = randint(1, MAX_INT), randint(1, MAX_INT)
    print('I am thinking of two integers. What is their sum?')
    correct_answer = sum((num_1, num_2))
    answer_string = input('Please enter your answer here: ')
    alphabet = ''

    if any(c in ' \'"()' for c in answer_string):
        print('Parentheses and spaces not supported.')
        print('You lose!')
        exit(1)

    answer = eval(answer_string, {'__builtins__': {}})
    print(f'The two integers were {num_1} and {num_2}. The correct answer was {correct_answer}.')
    print('You win!' if answer == correct_answer else 'You lose!')

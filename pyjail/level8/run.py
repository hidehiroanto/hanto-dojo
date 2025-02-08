#!/usr/bin/exec-suid -- /usr/bin/python3 -I

from os.path import getsize
from random import randint
from sys import modules

MAX_INT = 1 << 0x40

if __name__ == '__main__':
    print(f'The flag is {getsize('/flag')} characters long.')
    num_1, num_2 = randint(1, MAX_INT), randint(1, MAX_INT)
    print('I am thinking of two integers. What is their sum?')
    correct_answer = sum((num_1, num_2))
    answer_string = input('Please enter your answer here: ')

    eval, print = eval, print
    modules.clear()
    __builtins__.__dict__.clear()
    del getsize, randint, modules, __loader__
    __builtins__ = None

    answer = eval(answer_string)
    print(f'The two integers were {num_1} and {num_2}. The correct answer was {correct_answer}.')
    print('You win!' if answer == correct_answer else 'You lose!')

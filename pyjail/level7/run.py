#!/usr/bin/exec-suid -- /usr/bin/python3 -I

for global_variable in list(globals().values()):
    if hasattr(global_variable, 'open'):
        delattr(global_variable, 'open')

from os.path import getsize
from random import randint

MAX_INT = 1 << 0x40

if __name__ == '__main__':
    print(f'The flag is {getsize("/flag")} characters long.')
    num_1, num_2 = randint(1, MAX_INT), randint(1, MAX_INT)
    print('I am thinking of two integers. What is their sum?')
    answer = eval(input('Please enter your answer here: '))
    print(f'The two integers were {num_1} and {num_2}. The correct answer was {sum((num_1, num_2))}.')
    print('You win!' if answer == sum((num_1, num_2)) else 'You lose!')

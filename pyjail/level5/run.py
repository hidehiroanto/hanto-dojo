#!/usr/bin/exec-suid -- /usr/bin/python3 -I

import random

MAX_INT = 1 << 0x40

if __name__ == '__main__':
    with open('/flag') as f:
        print(f'The flag is {len(f.read())} characters long.')
    open = None
    num_1, num_2 = random.randint(1, MAX_INT), random.randint(1, MAX_INT)
    print('I am thinking of two integers. What is their sum?')
    answer = eval(input('Please enter your answer here: '))
    print(f'The two integers were {num_1} and {num_2}. The correct answer was {sum((num_1, num_2))}.')
    print('You win!' if answer == sum((num_1, num_2)) else 'You lose!')

#!/usr/bin/exec-suid -- /usr/bin/python3 -I

import os
import random

MAX_INT = 49999

def lose():
    print('You lose! No flag for you!')
    print('I will now delete the flag to mitigate brute forcing.')
    os.remove('/flag')
    exit(1)

def win():
    with open('/flag') as f:
        print(f'You win! The flag is: {f.read().strip()}')
    exit(0)

if __name__ == '__main__':
    print(f'The flag is {os.path.getsize('/flag')} characters long.')
    num_1, num_2 = random.randint(1, MAX_INT), random.randint(1, MAX_INT)
    print(f'I am thinking of two integers, each between 1 and {MAX_INT}. What is their sum?')
    answer_string = input('Please enter your answer here: ')
    if len(answer_string) > len(str(2 * MAX_INT)):
        print(f'The sum is less than {2 * MAX_INT}.')
        lose()
    answer = eval(answer_string)
    print(f'The two integers were {num_1} and {num_2}. The correct answer was {sum((num_1, num_2))}.')
    win() if answer == sum((num_1, num_2)) else lose()

#!/usr/bin/exec-suid -- /usr/bin/python3 -I

import os
import random

MAX_INT = 499

if __name__ == '__main__':
    a, b = random.randint(1, MAX_INT), random.randint(1, MAX_INT)
    print(f'I am thinking of two integers, each between 1 and {MAX_INT}.')
    print('They are named a and b. What is their sum?')
    answer_string = input('Please enter your answer here: ')
    if len(answer_string) > len(str(2 * MAX_INT)):
        print(f'The sum is less than {2 * MAX_INT + 1}.')
        print('You lose! No flag for you!')
        exit(1)
    answer = eval(answer_string)
    print(f'You answered: {answer}')
    print(f'The two integers were {a} and {b}. The correct answer was {sum((a, b))}.')
    if answer == sum((a, b)):
        with open('/flag') as f:
            print(f'You win! The flag is: {f.read().strip()}')
    else:
        print('You lose! No flag for you!')
        print('I will now delete the flag to mitigate brute forcing.')
        os.remove('/flag')

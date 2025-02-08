#!/usr/bin/exec-suid -- /usr/bin/python3 -I

import random

MAX_INT = 49999999999

if __name__ == '__main__':
    with open('/flag') as f:
        flag = f.read()
        print(f'The flag is {len(flag)} characters long.')
    num_1, num_2 = random.randint(1, MAX_INT), random.randint(1, MAX_INT)
    print(f'I am thinking of two integers, each between 1 and {MAX_INT}. What is their sum?')
    answer_string = input('Please enter your answer here: ')
    if len(answer_string) > len(str(2 * MAX_INT)):
        print(f'The sum is less than {2 * MAX_INT}.')
        print('You lose!')
        exit(1)
    answer = eval(answer_string)
    print(f'The two integers were {num_1} and {num_2}. The correct answer was {sum((num_1, num_2))}.')
    print('You win!' if answer == sum((num_1, num_2)) else 'You lose!')

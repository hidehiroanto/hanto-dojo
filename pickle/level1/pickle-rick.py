#!/usr/bin/exec-suid -- /usr/bin/python3 -I

import base64
from math import inf
import os
import pickle
from PIL import Image
from time import sleep, time

COLOR_GREEN = '\x1b[38;5;46m'
COLOR_RESET = '\x1b[0m'

WELCOME = fr'''{COLOR_GREEN}
        __        __   _                            _        
        \ \      / /__| | ___ ___  _ __ ___   ___  | |_ ___  
         \ \ /\ / / _ \ |/ __/ _ \| '_ ` _ \ / _ \ | __/ _ \ 
          \ V  V /  __/ | (_| (_) | | | | | |  __/ | || (_) |
           \_/\_/ \___|_|\___\___/|_| |_| |_|\___|  \__\___/ 
{COLOR_RESET}'''

CHALLENGE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
GHERKIN_JAR = os.path.join(CHALLENGE_DIRECTORY, 'jar')
BURP = '**BURRRRRP**'

BIG_SLEEP = 1.0
SMALL_SLEEP = 0.05

EMPTY = 0
PLAYER_MORTY = 1
PLAYER_AI = 2
PLAYERS = {EMPTY: '     ', PLAYER_MORTY: 'MORTY', PLAYER_AI: 'MY AI'}

def clear_screen():
    print('\x1b[H\x1b[2J\x1b[3J', end='')

def print_welcome():
    for line in WELCOME.split('\n'):
        print(line)
        sleep(SMALL_SLEEP)
    sleep(BIG_SLEEP)

    color_char = lambda char, pixel: f'\x1b[38;2;%d;%d;%dm{char}\x1b[0m' % pixel[:3] if pixel[3] else ' '
    with Image.open(os.path.join(CHALLENGE_DIRECTORY, 'images', 'pickle-rick.png')) as picture_rick:
        for y in range(picture_rick.height):
            print(''.join(color_char('OX'[(x ^ y) & 1], picture_rick.getpixel((x, y))) for x in range(picture_rick.width)))
            sleep(SMALL_SLEEP)
    sleep(BIG_SLEEP)
    print(f"{COLOR_GREEN}Now listen, I need your help Morty, {BURP} I'm a pickle again.")
    print(f"I need you to play a game of Tic-Tac-Toe {BURP} against my rogue AI.")
    print(f"If you win, it'll spit out {BURP} the anti-pickle serum.")
    print(f"With the serum, I can turn back into a human {BURP} without this green text.{COLOR_RESET}")

def print_simple_board(board):
    print('            Board:        \n')
    print('      0       1       2   \n')
    print('          |       |       ')
    print('0   ' + ' | '.join(map(PLAYERS.get, board[0])))
    print('          |       |       ')
    print('   -------+-------+-------')
    print('          |       |       ')
    print('1   ' + ' | '.join(map(PLAYERS.get, board[1])))
    print('          |       |       ')
    print('   -------+-------+-------')
    print('          |       |       ')
    print('2   ' + ' | '.join(map(PLAYERS.get, board[2])))
    print('          |       |       \n')

def print_menu():
    print('Menu:')
    print('1) Move Morty')
    print('2) Save gherkin')
    print('3) Quit')

def load_gherkin():
    new_board = [[EMPTY for _ in range(3)] for _ in range(3)]
    load_choice = input('\nWould you like to load a gherkin from the jar? (y/N): ').strip()
    if load_choice.lower().startswith('y'):
        if os.path.isdir(GHERKIN_JAR) and os.listdir(GHERKIN_JAR):
            print('List of gherkins in the jar:')
            for gherkin_name in os.listdir(GHERKIN_JAR):
                with open(os.path.join(GHERKIN_JAR, gherkin_name)) as gherkin_file:
                    print(f'{gherkin_name}: {COLOR_GREEN}{gherkin_file.read()}{COLOR_RESET}')

        gherkin = input('Enter gherkin: ').strip()
        if gherkin:
            try:
                decoded_gherkin = base64.b64decode(gherkin)
                if len(decoded_gherkin) > len(pickle.dumps(new_board)):
                    raise ValueError('Gherkin is too large')
                saved_board = pickle.loads(decoded_gherkin)
                if not isinstance(saved_board, list) or len(saved_board) != 3:
                    raise ValueError('Board must be a list of 3 rows')
                if not all(isinstance(row, list) and len(row) == 3 and all(player in PLAYERS for player in row) for row in saved_board):
                    raise ValueError(f'Each row must be a list of 3 integers between {min(PLAYERS)} and {max(PLAYERS)}')
                print('Gherkin loaded successfully.')
                return saved_board
            except Exception as e:
                print(f'Error loading gherkin: {e}')
        else:
            print('No gherkin entered.')
    print('Starting new game...')
    return new_board

def save_gherkin(board, gherkin_name):
    try:
        if not os.path.isdir(GHERKIN_JAR):
            os.mkdir(GHERKIN_JAR)
        gherkin_path = os.path.join(GHERKIN_JAR, gherkin_name)
        print(f'Preserving gherkin at {COLOR_GREEN}{gherkin_path}{COLOR_RESET} ...')
        with open(gherkin_path, 'wb') as gherkin_file:
            gherkin_file.write(base64.b64encode(pickle.dumps(board)))
        print(f'Gherkin preserved at {COLOR_GREEN}{gherkin_path}{COLOR_RESET} successfully.')
    except Exception as e:
        print(f'Error preserving gherkin file: {e}')

def display_gherkin(board):
    display_choice = input('Would you like to display this gherkin? (y/N): ').strip()
    if display_choice.lower().startswith('y'):
        try:
            print('Generating gherkin...')
            gherkin = base64.b64encode(pickle.dumps(board)).decode()
            print(f'Gherkin: {COLOR_GREEN}{gherkin}{COLOR_RESET}')
        except Exception as e:
            print(f'Error displaying gherkin: {e}')

def check_win(board, player):
    if any(all(board[row][col] == player for col in range(3)) for row in range(3)):
        return True
    if any(all(board[row][col] == player for row in range(3)) for col in range(3)):
        return True
    return all(board[i][i] == player for i in range(3)) or all(board[i][~i] == player for i in range(3))

def check_full(board):
    return all(all(board[row][col] != EMPTY for col in range(3)) for row in range(3))

def minimax(board, maximize):
    if check_win(board, PLAYER_AI):
        return 1
    if check_win(board, PLAYER_MORTY):
        return -1
    if check_full(board):
        return 0
    if maximize:
        best_score = -inf
        for row in range(3):
            for col in range(3):
                if board[row][col] == EMPTY:
                    board[row][col] = PLAYER_AI
                    score = minimax(board, False)
                    board[row][col] = EMPTY
                    best_score = max(score, best_score)
        return best_score
    else:
        best_score = inf
        for row in range(3):
            for col in range(3):
                if board[row][col] == EMPTY:
                    board[row][col] = PLAYER_MORTY
                    score = minimax(board, True)
                    board[row][col] = EMPTY
                    best_score = min(score, best_score)
        return best_score

def get_ai_move(board):
    best_score = -inf
    best_move = None
    for row in range(3):
        for col in range(3):
            if board[row][col] == EMPTY:
                board[row][col] = PLAYER_AI
                score = minimax(board, False)
                board[row][col] = EMPTY
                if score > best_score:
                    best_score = score
                    best_move = (row, col)
    return best_move

def move_player(board, row, col):
    board[row][col] = PLAYER_MORTY
    if not check_win(board, PLAYER_MORTY) and not check_full(board):
        print('Waiting for AI move...')
        ai_row, ai_col = get_ai_move(board)
        board[ai_row][ai_col] = PLAYER_AI

def check_endgame(board):
    if check_win(board, PLAYER_MORTY):
        print(f"{COLOR_GREEN}You won, Morty! {BURP}{COLOR_RESET}")
        print(f"I'm not a pickle anymore, Morty! {BURP}")
        return True
    if check_win(board, PLAYER_AI):
        print(f"{COLOR_GREEN}You lost, Morty! {BURP}")
        print(f"Can't believe I'm still a pickle because my idiot grandson {BURP} can't even beat my AI.{COLOR_RESET}")
        return True
    if check_full(board):
        print(f"{COLOR_GREEN}It's a tie, Morty! {BURP}")
        print(f"A tie is as bad as losing, Morty! {BURP}{COLOR_RESET}")
        return True
    return False

if __name__ == '__main__':
    print_welcome()
    board = load_gherkin()
    while True:
        sleep(BIG_SLEEP)
        clear_screen()
        print_simple_board(board)
        if check_endgame(board):
            display_gherkin(board)
            break
        print_menu()
        menu_option = input('Enter menu option number: ').strip()
        if menu_option == '1':
            print(f'{COLOR_GREEN}OK Morty, {BURP} where are you going to move?{COLOR_RESET}')
            row = input('Enter row number (0-2): ').strip()
            if row not in ['0', '1', '2']:
                print(f"{COLOR_GREEN}That's not a valid row number, Morty. {BURP}{COLOR_RESET}")
            else:
                col = input('Enter column number (0-2): ').strip()
                if col not in ['0', '1', '2']:
                    print(f"{COLOR_GREEN}That's not a valid column number, Morty. {BURP}{COLOR_RESET}")
                elif board[int(row)][int(col)] == EMPTY:
                    move_player(board, int(row), int(col))
                else:
                    print(f"{COLOR_GREEN}Someone's already there, Morty. {BURP}{COLOR_RESET}")
        elif menu_option == '2':
            print(f'{COLOR_GREEN}Good choice Morty, {BURP} stash me away somewhere safe.{COLOR_RESET}')
            save_gherkin(board, f'gherkin_{int(time())}')
        elif menu_option == '3':
            print(f"{COLOR_GREEN}Fine then, go away loser. Come back when you're ready. {BURP}{COLOR_RESET}")
            break
        else:
            print(f"{COLOR_GREEN}That's not a valid menu option, Morty. {BURP}{COLOR_RESET}")
    print('Goodbye Morty!')

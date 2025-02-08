#!/usr/bin/exec-suid -- /usr/bin/python3 -I

from angr import Project
import os
from time import time

CHALLENGE_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
BINARY_DIRECTORY = os.path.join(CHALLENGE_DIRECTORY, 'bin')
PROJECT_DIRECTORY = os.path.join(CHALLENGE_DIRECTORY, 'projects')

def load_project() -> Project:
    print('Welcome to the angr helper!')
    choice = input('Load stored project? (y/N): ')
    if choice.strip().lower().startswith('y'):
        if not os.path.isdir(PROJECT_DIRECTORY):
            os.mkdir(PROJECT_DIRECTORY)
        project_list = sorted(os.listdir(PROJECT_DIRECTORY))
        print('List of projects:\n' + '\n'.join(project_list) + '\n')

        project_name = input(f'Enter project name: ').strip()
        if project_name:
            project_path = os.path.realpath(os.path.join(PROJECT_DIRECTORY, project_name))
            if os.path.isfile(project_path):
                return Project._load(project_path)
            else:
                print(f'File {project_path} does not exist.')
        else:
            print(f'No project name given.')

        print(f'Loading most recent project in {PROJECT_DIRECTORY} instead...')
        if project_list:
            sorted_project_list = sorted(project_list, key=lambda f: int(f.split('_')[-1]))
            return Project._load(os.path.join(PROJECT_DIRECTORY, sorted_project_list[-1]))
        else:
            print(f'There are no projects in {PROJECT_DIRECTORY} right now.')

    print('Starting new project...')
    binary_name = input(f'Enter binary name: ').strip()
    if binary_name:
        binary_path = os.path.realpath(os.path.join(BINARY_DIRECTORY, binary_name))
        if os.path.isfile(binary_path):
            return Project(binary_path, auto_load_libs=False)
        else:
            print(f'File {binary_path} does not exist.')
    else:
        print(f'No binary name given.')

    print('Loading default binary instead...')
    if not os.path.isdir(BINARY_DIRECTORY):
        os.mkdir(BINARY_DIRECTORY)
    binary_list = [os.path.join(BINARY_DIRECTORY, f) for f in sorted(os.listdir(BINARY_DIRECTORY))]
    if binary_list:
        return Project(binary_list[0], auto_load_libs=False)
    else:
        print(f'There are no binaries in {BINARY_DIRECTORY} right now.')
        return None

def store_project(project: Project) -> None:
    choice = input('Store project to file for later use? (y/N): ').strip()
    if choice.lower().startswith('y'):
        if not os.path.isdir(PROJECT_DIRECTORY):
            os.mkdir(PROJECT_DIRECTORY)
        project_name = f'{os.path.basename(project.filename)}_{int(time())}'
        project._store(os.path.join(PROJECT_DIRECTORY, project_name))

def get_conditions() -> tuple:
    choice = input('Manually enter addresses? (y/N): ').strip()
    if choice.lower().startswith('y'):
        try:
            win_addresses = input('Enter a list of win addresses, separated by commas: ')
            lose_addresses = input('Enter a list of lose addresses, separated by commas: ')
            win_list = [int(i, 0) for i in win_addresses.split(',')] if win_addresses else None
            lose_list = [int(i, 0) for i in lose_addresses.split(',')] if lose_addresses else None
            return win_list, lose_list
        except ValueError as e:
            print(f'Invalid address: {e}')

    print('Enabling lambda mode...')
    success_words = [word.encode() for word in input('Enter any words found only in success messages, separated by spaces: ').split()]
    failure_words = [word.encode() for word in input('Enter any words found only in failure messages, separated by spaces: ').split()]
    success_function = (lambda s: any(word in s.posix.dumps(1).split() for word in success_words)) if success_words else None
    failure_function = (lambda s: any(word in s.posix.dumps(1).split() for word in failure_words)) if failure_words else None
    return success_function, failure_function

if __name__ == '__main__':
    try:
        project = load_project()
        if project:
            find_condition, avoid_condition = get_conditions()
            manager = project.factory.simulation_manager(project.factory.entry_state())
            manager.explore(find=find_condition, avoid=avoid_condition)
            if manager.found:
                print(f'Password found: {manager.found[0].posix.dumps(0).decode()}')
            else:
                print('Password not found. Try again with different parameters.')
                store_project(project)
        else:
            print('Unable to load project. Please contact the developer.')
    except Exception as e:
        print(f'Something went wrong: {e}')
        exit(1)

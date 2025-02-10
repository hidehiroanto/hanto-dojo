#!/usr/bin/exec-suid --real -- /usr/bin/sage --nodotsage

import six

base_url = 'http://myoboku.zan'

path_table = '''
 # |　数　| English | rōmaji     |　漢字　　| संस्कृतम्
---+ーーー+---------+------------+ーーーーー+-----------
 1 |　壱　| Deva    | tendō      |　天道　　| देव पथ
 2 |　弐　| Asura   | shuradō    |　修羅道　| असुर पथ
 3 |　参　| Human   | ningendō   |　人間道　| मनुष्य पथ
 4 |　四　| Animal  | chikushōdō |　畜生道　| तिर्यग्योनि पथ
 5 |　五　| Preta   | gakidō     |　餓鬼道　| प्रेत पथ
 6 |　六　| Naraka  | jigokudō   |　地獄道　| नरक पथ
 7 |　七　| Outer   | gedō       |　外道　　| तीर्थिक पथ
'''

paths = {'1': 'ten', '2': 'shura', '3': 'ningen', '4': 'chikusho', '5': 'gaki', '6': 'jigoku', '7': 'ge'}

if __name__ == '__main__':
    print('I am the Sage of Six Paths. Welcome to the bhavachakra of eternal suffering!')
    while True:
        print('List of available paths:')
        print(path_table)
        option = input('Enter path number, or q to quit: ').strip()
        if option in paths:
            try:
                load(six.moves.urllib.parse.urljoin(base_url, os.path.join('.sage', 'paths', f'{paths[option]}.do')))
            except Exception as e:
                print(f'Error: {e}')
            print('The wheel of saṃsāra turns again...')
        elif option.lower().startswith('q'):
            break
        else:
            print('Invalid option.')
    print('You have achieved nirvana and escaped the cycle of saṃsāra.')

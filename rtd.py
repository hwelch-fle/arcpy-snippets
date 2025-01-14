import random

dice = {
    1: '⚀',
    2: '⚁',
    3: '⚂',
    4: '⚃',
    5: '⚄',
    6: '⚅'
}

def get_random_dice(count: int=6):
    return ','.join([dice[random.randint(1, 6)] for _ in range(count)])

def rtd():
    while response := input('Roll the dice? (y/n): ').lower():
        match response:
            case 'y':
                print(f'({get_random_dice()})', end='\r')
            case 'n':
                break
            case _:
                print('Invalid choice. (y/n)')

    print('\nGoodbye!')
    
if __name__ == '__main__':
    rtd()
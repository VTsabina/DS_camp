class Must_read:
    with open('data.csv', 'r', encoding='utf-8') as source:
        text = source.readlines()
        print(''.join(text))


if __name__ == '__main__':
    reader = Must_read()

import sys

def shifter(ch, shift):
    num = ord(ch) + shift
    if ord(ch) in range(65, 91):
        if num > 90:
            num -= 26
        elif num < 65:
            num += 26
    elif ord(ch) in range(97, 123):
        if num > 122:
            num -= 26
        elif num < 97:
            num += 26
    return chr(num)

def encoder(text, shift):
    res = ''
    for ch in text:
        if ch.isalpha():
            ch = shifter(ch, shift)
        res += ch
    return res

def decoder(text, shift):
    res = ''
    for ch in text:
        if ch.isalpha():
            ch = shifter(ch, -shift)
        res += ch
    return res

def get_task(task, text, shift):
    if not text.isascii():
        raise ValueError("The script does not support your language yet")
    res = ''
    if task == 'encode':
        res = encoder(text, int(shift))
    elif task == 'decode':
        res = decoder(text, int(shift))
    else:
        res = 'Wrong command. Please, choose one option: encode or decode.'
    return res


if __name__ == '__main__':
    if len(sys.argv) == 4:
        print(get_task(sys.argv[1], sys.argv[2], sys.argv[3]))
    else:
        raise ValueError("An incorrect number of arguments is given")
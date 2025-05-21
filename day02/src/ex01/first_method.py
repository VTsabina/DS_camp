class Research:

    def file_reader(self):
        with open('data.csv', 'r', encoding='utf-8') as source:
            text = source.readlines()
            return ''.join(text)


if __name__ == '__main__':
    reader = Research()
    print(reader.file_reader())

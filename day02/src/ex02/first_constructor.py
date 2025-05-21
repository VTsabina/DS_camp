import sys
import os


class Research:
    def __init__(self, path):
        self.filepath = path

    def file_reader(self):
        with open(self.filepath, 'r', encoding='utf-8') as source:
            header = source.readline()
            self.check_header(header)
            text = source.readlines()
            self.check_content(text)
            return header + ''.join(text)

    def check_header(self, header):
        if header.partition(',')[1] != ',':
            raise NameError("Wrong separator in header.")
        elif len(header.split(',')) != 2:
            raise NameError('Incorrect number of fieldnames in header.')

    def check_content(self, text):
        for line in text:
            if len(line.strip('\n')) != 3:
                raise TypeError("Incorrect number of fields.")
            elif line[1] != ',':
                raise SyntaxError("Wrong separator.")
            elif line[0] not in ('0', '1') or line[2] not in ('0', '1'):
                raise ValueError("Forbidden value.")
            elif line[0] == line[2]:
                raise ValueError("Head and tail can't have the same value.")


if __name__ == '__main__':
    reader = Research('data.csv')
    try:
        print(reader.file_reader())
    except NameError:
        print("Header must contain two strings delimited by a comma")
    except SyntaxError:
        print("Separator must be comma ','")
    except TypeError:
        print("Line must contain two integers, separated by comma")
    except ValueError:
        print("The line can only contain 1 (ones) and 0 (zeros), both fields can't have the same value.")
    except Exception as e:
        print(f"Something went wrong: {e}")

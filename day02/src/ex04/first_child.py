import sys
from random import randint


class Research:
    def __init__(self, path):
        self.filepath = path

    def file_reader(self, has_header=True):
        res = []
        with open(self.filepath, 'r', encoding='utf-8') as source:
            if has_header:
                header = source.readline()
                self.check_header(header)
            text = source.readlines()
            self.check_content(text)
            for item in text:
                res.append([int(i) for i in item.split(',')])
        return res

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

    class Calculations:
        def __init__(self, file_contents):
            self.data = file_contents

        def counts(self):
            heads, tails = 0, 0
            for item in self.data:
                if item[0] == 1:
                    heads += 1
                else:
                    tails += 1
            return heads, tails

        def fractions(self):
            heads, tails = self.counts()
            sum = heads + tails
            heads_percentage = heads / sum * 100
            tails_percentage = tails / sum * 100
            return heads_percentage, tails_percentage


class Analytics(Research.Calculations):
    def predict_random(self, num):
        res = []
        for i in range(num):
            head = randint(0, 1)
            tail = 1 - head
            res.append([head, tail])
        return res

    def predict_last(self):
        return self.data[-1]


if __name__ == '__main__':
    reader = Research('data.csv')
    try:
        text = reader.file_reader()
        print(text)
    except NameError:
        print("FileFormatError: Header must contain two strings delimited by a comma")
    except SyntaxError:
        print("FileFormatError: Separator must be comma ','")
    except TypeError:
        print("FileFormatError: Line must contain two integers, separated by comma")
    except ValueError:
        print("FileFormatError: The line can only contain 1 (ones) and 0 (zeros), both fields can't have the same value.")
    except Exception as e:
        print(f"Something went wrong! Check this: {e}")
    else:
        try:
            analysis = Analytics(text)
            print(*analysis.counts())
            print(*analysis.fractions())
            print(analysis.predict_random(3))
            print(analysis.predict_last())
        except Exception as e:
            print(f"Something went wrong! Check this: {e}")

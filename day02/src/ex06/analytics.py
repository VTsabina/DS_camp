import os
from random import randint
import logging
import requests
logging.basicConfig(level=logging.INFO, filename="analytics.log", filemode='w',
                    format="%(asctime)s %(levelname)s %(message)s")


class Research:
    def __init__(self, path):
        self.filepath = path
        logging.info("Created an example of Research class")

    def file_reader(self, has_header=True):
        logging.info(
            f"Research.file_reader() was called: Reading the contents of {self.filepath}. The has_header parameter is set to {has_header}")
        res = []
        with open(self.filepath, 'r', encoding='utf-8') as source:
            if has_header:
                header = source.readline()
                self.check_header(header)
            text = source.readlines()
            self.check_content(text)
            for item in text:
                res.append([int(i) for i in item.split(',')])
            col = len(res)
            logging.info(f"{col} items were edded to result list")
        return res

    def check_header(self, header):
        logging.info(
            "Research.check_header() was called: Checking format of file header")
        sep = header.partition(',')[1]
        size = len(header.split(','))
        if sep != ',':
            logging.error(f"Wrong separator in header: {sep}")
            raise NameError("Wrong separator in header.")
        elif size != 2:
            logging.error(
                f"Incorrect number of fieldnames in header: {size} given, 2 allowed")
            raise NameError('Incorrect number of fieldnames in header.')

    def check_content(self, text):
        logging.info(
            "Research.check_content() was called: Checking format of file contents")
        i = 0
        for line in text:
            i += 1
            size = len(line.strip('\n'))
            if size != 3:
                logging.error(
                    f"Line {i}. Incorrect number of fields: {size} given, 2 allowed")
                raise TypeError("Incorrect number of fields.")
            elif line[1] != ',':
                logging.error(f"Line {i}. Wrong separator: {line[1]}")
                raise SyntaxError("Wrong separator.")
            elif line[0] not in ('0', '1') or line[2] not in ('0', '1'):
                logging.error(
                    f"Line {i}. Forbidden value: {line[0]} and {line[2]} were given, 1 or 0 allowed")
                raise ValueError("Forbidden value.")
            elif line[0] == line[2]:
                logging.error(
                    f"Line {i}. Head and tail can't have the same value: {line[0]}")
                raise ValueError("Head and tail can't have the same value.")

    def get_id(self):
        TOKEN = "7290463375:AAFb5pUg1Ws6Haiwhz7dw8Z1uDzxG7cDWzI"
        url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
        print(requests.get(url).json())

    def report_tg(self, report_result):
        if report_result == True:
            message = 'The report has been successfully created'
        else:
            message = 'The report hasn’t been created due to an error'
        TOKEN = "7290463375:AAFb5pUg1Ws6Haiwhz7dw8Z1uDzxG7cDWzI"
        chat_id = "1133163052"
        url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
        requests.get(url).json()

    class Calculations:
        def __init__(self, file_contents):
            logging.info(
                "Created an example of Calculation or Analytics class")
            self.data = file_contents

        def counts(self, data=None):
            logging.info(
                "Calculations.counts() was called: Calculating the counts of heads and tails")
            if data == None:
                data = self.data
                logging.info("Working with self.data")
            else:
                logging.info("Working with given parameter")
            heads, tails = 0, 0
            for item in data:
                if item[0] == 1:
                    heads += 1
                else:
                    tails += 1
            logging.info(f"{heads} heads, {tails} tailes recognized")
            return heads, tails

        def fractions(self):
            logging.info(
                "Calculations.fractions() was called: Calculating percentage of heads and tails")
            heads, tails = self.counts()
            sum = heads + tails
            heads_percentage = heads / sum * 100
            tails_percentage = tails / sum * 100
            logging.info(
                f"Calculated {heads_percentage}% of heads and {tails_percentage}% of tails")
            return heads_percentage, tails_percentage


class Analytics(Research.Calculations):
    def predict_random(self, num):
        logging.info(
            f"Analytics.predict_random() was called: Making forecast for next {num} observations")
        res = []
        for i in range(num):
            head = randint(0, 1)
            tail = 1 - head
            res.append([head, tail])
        logging.info(f"Forecast for {num} observations done")
        return res

    def predict_last(self):
        last = self.data[-1]
        logging.info(
            f"Analytics.predict_last() was called: Getting last element in heads and tailes data: {last}")
        return last

    def save_file(self, data, filename, ext):
        dest = filename + '.' + ext
        logging.info(
            f"Analytics.save_file() was called: Saving the report in {dest} file")
        with open(dest, 'w', encoding='utf-8') as report:
            report.write(data)
        logging.info("Report saved successfully")

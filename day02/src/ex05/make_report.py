import os
from random import randint
import analytics as a
import config

if __name__ == '__main__':
    reader = a.Research(config.filename)
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
            analysis = a.Analytics(text)
            heads, tails = analysis.counts()
            h_per, t_per = analysis.fractions()
            prediction = analysis.predict_random(config.num_of_steps)
            last = analysis.predict_last()
            h_pred, t_pred = analysis.counts(prediction)
            print(heads, tails)
            print(h_per, t_per)
            print(prediction)
            print(last)
            data = config.report_template.format(len(text), tails, heads, format(
                t_per, '.2f'), format(h_per, '.2f'), config.num_of_steps, t_pred, h_pred)
            analysis.save_file(data, config.report_name, config.report_ext)
        except Exception as e:
            print(f"Something went wrong! Check this: {e}")

def spliter(csv_string):
    res = ''
    quotes = False
    for char in csv_string:
        if char == '"':
            quotes = not quotes
        if quotes == False and char == ',':
            char = '\t'
        res += char
    return res

def csv_to_tsv(source, res_file):
    with open(res_file, "w",encoding="utf-8") as tsv_data:
        with open(source, "r",encoding="utf-8") as csv_data:
            for elem in csv_data:
                tsv_data.write(spliter(elem))


if __name__ == '__main__':
    csv_to_tsv('ds.csv', 'ds.tsv')
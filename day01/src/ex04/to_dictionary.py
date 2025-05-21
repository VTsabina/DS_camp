def get_tuples():
    list_of_tuples = [
        ('Russia', '25'),
        ('France', '132'),
        ('Germany', '132'),
        ('Spain', '178'),
        ('Italy', '162'),
        ('Portugal', '17'),
        ('Finland', '3'),
        ('Hungary', '2'),
        ('The Netherlands', '28'),
        ('The USA', '610'),
        ('The United Kingdom', '95'),
        ('China', '83'),
        ('Iran', '76'),
        ('Turkey', '65'),
        ('Belgium', '34'),
        ('Canada', '28'),
        ('Switzerland', '26'),
        ('Brazil', '25'),
        ('Austria', '14'),
        ('Israel', '12')
    ]

    return list_of_tuples

def to_dict(list_of_tuples):
    res = dict()

    for item in list_of_tuples:
        if item[1] not in res.keys():
            res[item[1]] = []
        res[item[1]].append(item[0])

    return res

def print_formated(dictionary):
    for key, value in dictionary.items():
        for item in value:
            print(f"'{key}': '{item}'")


if __name__ == '__main__':
    print_formated(to_dict(get_tuples()))
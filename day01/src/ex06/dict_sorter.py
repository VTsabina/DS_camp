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

def make_dict(list_of_tuples):
    res = dict()
    for item in list_of_tuples:
        res[item[0]] = item[1]
    return res

def sort_and_print(countries):
    sorted_dict = sorted(countries.items(), key=lambda item: (-int(item[1]), item[0]))
    for item in sorted_dict:
        print(item[0])

if __name__ == '__main__':
    sort_and_print(make_dict(get_tuples()))
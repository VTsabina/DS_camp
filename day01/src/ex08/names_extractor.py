import sys

def make_tsv(filename):
    with open('employees.tsv', 'w', encoding='utf-8') as res:
        res.write('\t'.join(["Name", "Surname", "E-mail\n"]))
        with open(filename, 'r', encoding='utf-8') as source:
            for item in source.readlines():
                name, surname = item.split('@')[0].split('.')
                line = '\t'.join([name.title(), surname.title(), item])
                res.write(line)

if __name__ == '__main__':
    if len(sys.argv) == 2:
        make_tsv(sys.argv[1])
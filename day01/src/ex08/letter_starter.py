import sys

def start_letter(name):
    return f'Dear {name}, welcome to our team. We are sure that it will be a pleasure to work with you. That’s a precondition for the professionals that our company hires.'
    
def get_name(email):
    with open('employees.tsv', 'r', encoding='utf-8') as source:
        for item in source.readlines():
            info = item.split('\t')
            if info[2].strip('\n') == email:
                name = info[0]
                return name
    raise KeyError("Can't find the e-mail.")


if __name__ == '__main__':
    try:
        if len(sys.argv) == 2:
            print(start_letter(get_name(sys.argv[1])))
    except:
        print("Sorry, there's no person with this e-mail in employees' list.")
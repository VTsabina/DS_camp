import sys

def get_list(task):
    clients = ['andrew@gmail.com', 'jessica@gmail.com', 'ted@mosby.com', 
               'john@snow.is', 'bill_gates@live.com', 'mark@facebook.com', 
               'elon@paypal.com', 'jessica@gmail.com']
    participants = ['walter@heisenberg.com', 'vasily@mail.ru', 'pinkman@yo.org', 
                    'jessica@gmail.com', 'elon@paypal.com', 'pinkman@yo.org', 
                    'mr@robot.gov', 'eleven@yahoo.com']
    recipients = ['andrew@gmail.com', 'jessica@gmail.com', 'john@snow.is']

    if task == 'call_center':
        return set(clients), set(recipients)
    elif task == 'potential_clients':
        return set(clients), set(participants)
    elif task == 'loyalty_program':
        return set(clients), set(participants)


def call_center():
    clients, recipients = get_list('call_center')
    return list(clients.difference(recipients))


def potential_clients():
    clients, participants = get_list('potential_clients')
    return list(participants.difference(clients))

def loyalty_program():
    clients, participants = get_list('loyalty_program')
    return list(clients.difference(participants))

def perform_task(task: str):
    if task == 'call_center':
        task_result = call_center()
    elif task == 'potential_clients':
        task_result = potential_clients()
    elif task == 'loyalty_program':
        task_result = loyalty_program()
    else:
        raise ValueError("Wrong task!")
    return task_result

if __name__ == '__main__':
    if len(sys.argv) == 2:
        print(perform_task(sys.argv[1]))
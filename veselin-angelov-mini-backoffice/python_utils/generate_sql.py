import random
from datetime import timedelta, datetime
from random import randrange, randint
# import names
import string


statuses = ['COMPLETE', 'PENDING', 'FAILED']
types = ['ANNUAL', 'MONTHLY', 'DAILY']
methods = ['PayPal', 'MasterCard', 'VISA']


def random_date(start, end):
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return start + timedelta(seconds=random_second)


def users_table():
    users = 'INSERT INTO users("username") VALUES '
    for i in range(1000):
        users += f"('{names.get_first_name()}'), "

    users = users[:-2]
    users += ';'

    print(users)


def payment_methods_table():
    payment_methods = 'INSERT INTO payment_methods("name") VALUES '

    for method in methods:
        payment_methods += f"('{method}'), "

    payment_methods = payment_methods[:-2]
    payment_methods += ';'

    print(payment_methods)


def subscriptions_table():
    subscriptions = 'INSERT INTO subscriptions("name", "type", "amount") VALUES '

    for letter in list(string.ascii_uppercase):
        subscriptions += f"('{letter}', '{random.choice(types)}', '{'{:.2f}'.format(random.uniform(1, 100))}'), "

    subscriptions = subscriptions[:-2]
    subscriptions += ';'

    print(subscriptions)


def payments_table():
    d1 = datetime.strptime('1/1/2020 1:30 PM', '%m/%d/%Y %I:%M %p')
    d2 = datetime.now()

    payments = 'INSERT INTO payments("date", "amount", "status", "subscription_id", "payment_method_id", "user_id") VALUES '

    for i in range(100000):

        payments += f"('{random_date(d1, d2)}', '{'{:.2f}'.format(random.uniform(1, 100))}', '{random.choice(statuses)}'," \
                    f" '{random.randint(1, 26)}', '{random.randint(1, 3)}', '{random.randint(1, 1000)}'), "

    payments = payments[:-2]
    payments += ';'

    print(payments)


if __name__ == '__main__':
#     users_table()
#     payment_methods_table()
#     subscriptions_table()
    payments_table()

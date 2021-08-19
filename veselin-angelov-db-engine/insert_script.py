import random
import names

from test import DbEngineTest


test = DbEngineTest()

test.test_init_db()

for i in range(1000000):
    test.test_insert_db(i, names.get_first_name(), random.randint(1, 100), names.get_last_name())

import time

from main import DbEngine
from utilities import DataType
# from long_data import long_data


class DbEngineTest:
    engine = DbEngine()

    def test_init_db(self):
        self.engine.create_db('test-db2')
        self.engine.use_db('test-db2')

        table_data = {
            'id': DataType.INT,
            'name': DataType.TEXT,
            'age': DataType.INT,
            'description': DataType.TEXT
        }

        self.engine.create_table('table', table_data)

    def test_insert_db(self, id, name, age, description):
        # self.engine.use_db('test-db1')

        insert_data1 = {
            'id': id,
            'name': name,
            'age': age,
            'description': description
        }

        self.engine.insert('table', insert_data1)

    def test_select_all(self):
        self.engine.use_db('test-db2')
        for res in self.engine.select('table'):
            print(res)

    def test_select(self):
        self.engine.use_db('test-db2')

        criteria = {
            'id': 20000,
        }

        criteria1 = {
            'name': 'Leon',
        }

        for res in self.engine.select('table', criteria):
            print(res)

    def test_delete(self):
        self.engine.use_db('test-db1')

        criteria = {
            'name': 'Gosho',
        }

        self.engine.delete('table', criteria)

    def test_update(self):
        self.engine.use_db('test-db1')

        criteria = {
            'name': 'Joro',
        }

        values = {
            'name': 'Goshi',
        }

        self.engine.update('table', criteria, values)


if __name__ == '__main__':
    test = DbEngineTest()

    # test.test_init_db()
    # test.test_insert_db()
    b = time.time()
    test.test_select()
    print(time.time() - b)
    # test.test_delete()
    # test.test_update()
    # test.test_select_all()

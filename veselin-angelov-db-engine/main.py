import csv
import itertools
import os

from utilities import DataType, WrongAmountOfValuesError, TypesNotMatchError, LockFile


class DbEngine:
    DEFAULT_DB_DIR = '/home/veselin/Documents/databases/'
    db_directory = ''
    db_name = ''
    db_meta_file_dir = ''
    db_meta_file = ''
    db_table_data = {}

    def create_db(self, name: str):
        assert name is not None, 'Argument "name" is required!'

        directory = f'{self.DEFAULT_DB_DIR}{name}'
        meta_file_dir = f'{directory}/{name}.csv'

        try:
            os.mkdir(directory)
            open(meta_file_dir, 'x')

        except FileExistsError:
            print(f'Database {name} already exists')
            raise

        print(f'Created database {name}!')

    def use_db(self, name: str):
        assert name is not None, 'Argument "name" is required!'

        self.db_name = name
        self.db_directory = f'{self.DEFAULT_DB_DIR}{self.db_name}'
        self.db_meta_file_dir = f'{self.db_directory}/{self.db_name}.csv'
        LockFile.lock(self.db_meta_file_dir)
        self.db_meta_file = open(self.db_meta_file_dir, 'a+')
        self.db_meta_file.seek(0)
        reader = csv.reader(self.db_meta_file, delimiter=',')
        for row in reader:
            self.db_table_data[row[0]] = reader.line_num
        LockFile.unlock(self.db_meta_file_dir)

        print(f'Using database {name}')

    def create_table(self, name: str, data: dict):
        assert name is not None, 'Argument "name" is required!'
        assert data is not None, 'Argument "data" is required!'

        try:
            open(f'{self.db_directory}/table_{name}.csv', 'x')

        except FileExistsError:
            print(f'Cannot create table "{name}". Already exists!')
            raise

        LockFile.lock(self.db_meta_file_dir)

        writer = csv.writer(self.db_meta_file)
        data_row = []
        for key, value in data.items():
            data_row.append(key)
            data_row.append(value.name)

        writer.writerow([name, *data_row])
        self.db_meta_file.flush()

        print(f'Created table {name}!')

        self.db_meta_file.seek(0)
        reader = csv.reader(self.db_meta_file, delimiter=',')
        for row in reader:
            self.db_table_data[row[0]] = reader.line_num

        LockFile.unlock(self.db_meta_file_dir)

    def insert(self, table_name: str, values: dict):
        assert table_name is not None, 'Argument "table_name" is required!'
        assert values is not None, 'Argument "values" is required!'
        assert table_name in self.db_table_data, f'Table "{table_name}" not found!'

        self.db_meta_file.seek(0)
        table_schema = next(itertools.islice(csv.reader(self.db_meta_file), self.db_table_data[table_name] - 1, None))

        assert (len(table_schema) - 1) % 2 == 0, 'Columns and types count mismatch!'
        assert (len(table_schema) - 1) / 2 == len(values), \
            f'Expected {int((len(table_schema) - 1) / 2)} values, got {len(values)}'

        insert_data = []

        for index in range(1, len(table_schema), 2):
            value = values[table_schema[index]]
            value_type = getattr(DataType, table_schema[index + 1])

            assert type(value) == value_type.value, f'Received {type(value)}, expected {value_type.value}!'

            insert_data.append(value)

        insert_data.append('+')  # is deleted flag

        with open(f'{self.db_directory}/table_{table_name}.csv', 'a') as file:
            LockFile.lock(f'{self.db_directory}/table_{table_name}.csv')
            writer = csv.writer(file)
            writer.writerow(insert_data)
            LockFile.unlock(f'{self.db_directory}/table_{table_name}.csv')

        print('Inserted a row!')

    def _search(self, table_name: str, criteria: dict, line_numbers=False):
        with open(f'{self.db_directory}/table_{table_name}.csv', 'r') as file:
            reader = csv.reader(file)

            c_key = ''
            c_value = ''
            for key, value in criteria.items():
                c_key = key
                c_value = value

            LockFile.lock(self.db_meta_file_dir)
            self.db_meta_file.seek(0)
            table_schema = next(
                itertools.islice(csv.reader(self.db_meta_file), self.db_table_data[table_name] - 1, None))
            LockFile.unlock(self.db_meta_file_dir)

            table_schema_dict = {table_schema[i]: table_schema[i + 1] for i in range(1, len(table_schema), 2)}

            LockFile.lock(f'{self.db_directory}/table_{table_name}.csv')
            for row in reader:
                row_dict = {}
                index = 0
                for key, value in table_schema_dict.items():
                    value_type = getattr(DataType, value)
                    row_dict[key] = value_type.value(row[index])
                    index += 1

                if row_dict[c_key] == c_value:
                    if line_numbers:
                        yield reader.line_num

                    else:
                        yield row[:-1]

            LockFile.unlock(f'{self.db_directory}/table_{table_name}.csv')

    def select(self, table_name: str, criteria=None):
        assert table_name is not None, 'Argument "table_name" is required!'
        assert table_name in self.db_table_data, f'Table "{table_name}" not found!'

        if not criteria:
            with open(f'{self.db_directory}/table_{table_name}.csv', 'r') as file:
                LockFile.lock(f'{self.db_directory}/table_{table_name}.csv')
                reader = csv.reader(file)
                for row in reader:
                    yield row
                LockFile.unlock(f'{self.db_directory}/table_{table_name}.csv')

        else:
            # print(self._search(table_name, criteria))
            for row in self._search(table_name, criteria):
                yield row
            # return self._search(table_name, criteria)

    def delete(self, table_name: str, criteria: dict):
        assert table_name is not None, 'Argument "table_name" is required!'
        assert table_name in self.db_table_data, f'Table "{table_name}" not found!'

        # lines = self._search(table_name, criteria, line_numbers=True)
        # print(lines)
        # for line in lines:
        #     print(line)
        with open(f'{self.db_directory}/table_{table_name}.csv', 'a+') as file:
            for line in self._search(table_name, criteria, line_numbers=True):
                print(line)
                # LockFile.lock(f'{self.db_directory}/table_{table_name}.csv')

                file.seek(0)
                line_to_be_deleted = next(itertools.islice(csv.reader(file), line - 1, None))
                # line_to_be_deleted[-1] = '-'
                print(line_to_be_deleted)
                line_to_be_deleted[-1] = '-'
                # writer = csv.writer(file)
                # next(itertools.islice(writer, line - 1, None))
                # writer.writerow(line_to_be_deleted)  # TODO writer iter to line

                # LockFile.unlock(f'{self.db_directory}/table_{table_name}.csv')
                # pass  # TODO delete from file ?


def test():
    try:
        engine = DbEngine()

        # engine.create_db('test')
        engine.use_db('test')

        users = {
            'user_id': DataType.INT,
            'username': DataType.TEXT,
            'password': DataType.TEXT,
        }

        # engine.create_table('users', users)

        cars = {
            'car_id': DataType.INT,
            'model': DataType.TEXT,
        }

        # engine.create_table('cars', cars)

        tickets = {
            'ticket_id': DataType.INT,
            'name': DataType.TEXT,
            'reason': DataType.TEXT,
            'price': DataType.INT,
        }

        # engine.create_table('tickets', tickets)

        # *[1, 'vesko', 'vesko']

        user = {
            'user_id': 1,
            'username': 'vesko',
            'password': 'vesko',
        }

        user1 = {
            'user_id': 2,
            'username': 'tzetzo',
            'password': 'tzetzo',
        }

        user2 = {
            'user_id': 3,
            'username': 'daniel',
            'password': 'daniel',
        }

        user3 = {
            'user_id': 4,
            'username': 'momo',
            'password': 'momo',
        }

        user4 = {
            'user_id': 5,
            'username': 'aleks',
            'password': 'aleks',
        }

        user5 = {
            'user_id': 6,
            'username': 'obo',
            'password': 'obo'
        }

        # engine.insert('users', user)
        # engine.insert('users', user1)
        # engine.insert('users', user2)
        # engine.insert('users', user3)
        # engine.insert('users', user4)
        engine.insert('users1', user5)

        # engine.use_db('test')

        criteria = {
            'username': 'vesko',
        }

        engine.select('users', criteria)

    except Exception as e:
        print(e)
        raise


def test_select():
    engine = DbEngine()

    engine.use_db('test')

    criteria = {
        'username': 'obo',
    }

    # for row in engine.select('users'):
    #     print(row)

    # print(engine.select('users', criteria))
    for row in engine.select('users', criteria):
        print(row)


def test_delete():
    engine = DbEngine()

    engine.use_db('test')

    criteria = {
        'username': 'obo',
    }

    engine.delete('users', criteria)


if __name__ == '__main__':
    # test()
    # test_select()
    test_delete()

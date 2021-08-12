import csv
import itertools
import os

from utilities import DataType, WrongAmountOfValuesError, TypesNotMatchError


class DbEngine:
    DEFAULT_DB_DIR = '/home/veselin/Documents/databases/'
    db_directory = ''
    db_name = ''
    db_meta_file_dir = ''
    db_meta_file = ''
    db_table_data = {}

    def create_db(self, name):
        try:
            directory = f'{self.DEFAULT_DB_DIR}{name}'
            meta_file_dir = f'{directory}/{name}.csv'
            os.mkdir(directory)
            open(meta_file_dir, 'x')
            print(f'Created database {name}!')
        except FileExistsError:
            print(f'Database {name} already exists')

        except Exception as e:
            print(e)

    def use_db(self, name):
        try:
            self.db_name = name
            self.db_directory = f'{self.DEFAULT_DB_DIR}{self.db_name}'
            self.db_meta_file_dir = f'{self.db_directory}/{self.db_name}.csv'
            self.db_meta_file = open(self.db_meta_file_dir, 'a+')
            self.db_meta_file.seek(0)
            reader = csv.reader(self.db_meta_file, delimiter=',')
            for row in reader:
                self.db_table_data[row[0]] = reader.line_num

            print(f'Using database {name}')

        except Exception as e:
            print(e)

    def create_table(self, name, data):
        try:
            open(f'{self.db_directory}/table_{name}.csv', 'x')

            writer = csv.writer(self.db_meta_file)
            data_row = []
            for key, value in data.items():
                data_row.append(key)
                data_row.append(value.name)

            writer.writerow([name, *data_row])

            print(f'Created table {name}!')

            self.db_meta_file.seek(0)
            reader = csv.reader(self.db_meta_file, delimiter=',')
            for row in reader:
                self.db_table_data[row[0]] = reader.line_num

        except FileExistsError:
            print(f'Cannot create table "{name}". Already exists!')

        except Exception as e:
            print(e)

    def insert(self, table_name, values):
        try:
            if not self.db_table_data[table_name]:
                raise FileNotFoundError

            self.db_meta_file.seek(0)
            table_schema = next(itertools.islice(csv.reader(self.db_meta_file), self.db_table_data[table_name] - 1, None))

            if (len(table_schema) - 1) / 2 != len(values):
                raise WrongAmountOfValuesError

            insert_data = []

            for index in range(1, len(table_schema), 2):
                value = values[table_schema[index]]
                value_type = getattr(DataType, table_schema[index + 1])

                if type(value) != value_type.value:
                    raise TypesNotMatchError

                insert_data.append(value)

            with open(f'{self.db_directory}/table_{table_name}.csv', 'a') as file:
                writer = csv.writer(file)
                writer.writerow(insert_data)

            # insert between

        except WrongAmountOfValuesError:
            print(f'WrongAmountOfValuesError: Expected {int((len(table_schema) - 1) / 2)} arguments, got {len(values)}')

        except TypesNotMatchError:
            print('Types do not match the table row type')

        except FileNotFoundError:
            print(f'Table "{table_name}" does not exist!')

        except Exception as e:
            print(e)

    def _search(self, table_name, criteria):
        with open(f'{self.db_directory}/table_{table_name}.csv', 'r') as file:
            reader = csv.reader(file)

            c_key = ''
            c_value = ''
            for key, value in criteria.items():
                c_key = key
                c_value = value

            self.db_meta_file.seek(0)
            table_schema = next(
                itertools.islice(csv.reader(self.db_meta_file), self.db_table_data[table_name] - 1, None))

            table_schema_dict = {table_schema[i]: table_schema[i + 1] for i in range(1, len(table_schema), 2)}

            rows = []
            lines = []

            for row in reader:
                row_dict = {}
                index = 0
                for key, value in table_schema_dict.items():
                    value_type = getattr(DataType, value)
                    row_dict[key] = value_type.value(row[index])
                    index += 1

                if row_dict[c_key] == c_value:
                    rows.append(row)
                    lines.append(reader.line_num)

        return rows, lines

    def select(self, table_name, criteria=None):
        try:
            if not self.db_table_data[table_name]:
                raise FileNotFoundError

            if not criteria:
                with open(f'{self.db_directory}/table_{table_name}.csv', 'r') as file:
                    reader = csv.reader(file)
                    for row in reader:
                        print(row)

            else:
                print(self._search(table_name, criteria)[0])

        except FileNotFoundError:
            print(f'Table "{table_name}" does not exist!')

        except Exception as e:
            print(e)

    def delete(self, table_name, criteria):
        try:
            if not self.db_table_data[table_name]:
                raise FileNotFoundError

            lines = self._search(table_name, criteria)[1]
            with open(f'{self.db_directory}/table_{table_name}.csv', 'a') as file:
                for line in lines:
                    pass  # TODO delete from file ?

        except FileNotFoundError:
            print(f'Table "{table_name}" does not exist!')

        except Exception as e:
            print(e)


def test():
    engine = DbEngine()

    engine.create_db('test')
    engine.use_db('test')

    users = {
        'user_id': DataType.INT,
        'username': DataType.TEXT,
        'password': DataType.TEXT,
    }

    engine.create_table('users', users)

    cars = {
        'car_id': DataType.INT,
        'model': DataType.TEXT,
    }

    engine.create_table('cars', cars)

    tickets = {
        'ticket_id': DataType.INT,
        'name': DataType.TEXT,
        'reason': DataType.TEXT,
        'price': DataType.INT,
    }

    engine.create_table('tickets', tickets)

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

    engine.insert('users', user)
    engine.insert('users', user1)
    engine.insert('users', user2)
    engine.insert('users', user3)
    engine.insert('users', user4)

    # engine.use_db('test')

    criteria = {
        'username': 'vesko',
    }

    engine.select('users', criteria)


def test_select():
    engine = DbEngine()

    engine.use_db('test')

    criteria = {
        'user_id': 1,
    }

    engine.select('users', criteria)


if __name__ == '__main__':
    # test()
    test_select()

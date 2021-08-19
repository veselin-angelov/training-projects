import codecs
import io
import os

from utilities import DataType, LockFile, VeskoReaderWriter, MAX_META_CHARS, DELETED_CHARS, MAX_POINTER_CHARS


class DbEngine:
    DEFAULT_DB_DIR = '/home/veselin/Documents/databases/'
    META_DATA_LENGTH = 15
    CHUNK_SIZE = 10000
    db_directory = ''
    db_name = ''
    db_meta_file_dir = ''
    db_meta_file = ''
    db_table_data = {}

    def create_db(self, name: str):
        assert name is not None, 'Argument "name" is required!'

        directory = f'{self.DEFAULT_DB_DIR}{name}'
        meta_file_dir = f'{directory}/{name}.bin'

        try:
            os.mkdir(directory)
            open(meta_file_dir, 'xb')

        except FileExistsError:
            print(f'Database {name} already exists')
            raise

        print(f'Created database {name}!')

    def use_db(self, name: str):
        assert name is not None, 'Argument "name" is required!'

        self.db_name = name
        self.db_directory = f'{self.DEFAULT_DB_DIR}{self.db_name}'
        self.db_meta_file_dir = f'{self.db_directory}/{self.db_name}.bin'
        LockFile.lock(self.db_meta_file_dir)

        try:
            self.db_meta_file = open(self.db_meta_file_dir, 'rb+')
            self.db_table_data = VeskoReaderWriter.read_meta_file(self.db_meta_file, self.META_DATA_LENGTH)

        except Exception:
            LockFile.unlock(self.db_meta_file_dir)
            raise

        LockFile.unlock(self.db_meta_file_dir)

        print(f'Using database {name}')

    def create_table(self, name: str, data: dict):
        assert name is not None, 'Argument "name" is required!'
        assert data is not None, 'Argument "data" is required!'

        try:
            open(f'{self.db_directory}/table_{name}.bin', 'x')

            LockFile.lock(f'{self.db_directory}/table_{name}.bin')
            table = open(f'{self.db_directory}/table_{name}.bin', 'wb')
            VeskoReaderWriter.write_pointer_info(table, MAX_POINTER_CHARS * 2)
            LockFile.unlock(f'{self.db_directory}/table_{name}.bin')

        except FileExistsError:
            print(f'Cannot create table "{name}". Already exists!')
            raise

        LockFile.lock(self.db_meta_file_dir)

        try:
            data_row = [name]
            for key, value in data.items():
                data_row.append(key)
                data_row.append(value.name)

            line = VeskoReaderWriter.encode_line(data_row, self.META_DATA_LENGTH)

            self.db_meta_file.seek(0, io.SEEK_END)
            self.db_meta_file.write(line)

            print(f'Created table {name}!')

            self.db_meta_file.seek(0)
            self.db_table_data = VeskoReaderWriter.read_meta_file(self.db_meta_file, self.META_DATA_LENGTH)

        except Exception:
            LockFile.unlock(self.db_meta_file_dir)
            raise

        LockFile.unlock(self.db_meta_file_dir)

    def insert(self, table_name: str, values: dict, lock: bool = True):
        assert table_name is not None, 'Argument "table_name" is required!'
        assert values is not None, 'Argument "values" is required!'
        assert table_name in self.db_table_data, f'Table "{table_name}" not found!'
        assert len(self.db_table_data[table_name]) == len(values), \
            f'Expected {len(self.db_table_data[table_name])} values, got {len(values)}'

        table_data = self.db_table_data[table_name]
        insert_data = []

        for column_name in table_data:
            assert column_name in values, f'Value for {column_name} is missing!'
            assert isinstance(values[column_name], table_data[column_name][0].value), \
                f'Received {type(values[column_name])}, expected {table_data[column_name].value}!'

            insert_data.append(str(values[column_name]))

        encoded_line = VeskoReaderWriter.encode_line(insert_data, self.META_DATA_LENGTH)

        with open(f'{self.db_directory}/table_{table_name}.bin', 'rb+') as file:
            file.seek(VeskoReaderWriter.read_pointer_info(file))

            if lock:
                LockFile.lock(f'{self.db_directory}/table_{table_name}.bin')

                try:
                    print('writing')
                    file.write(encoded_line)
                    VeskoReaderWriter.write_pointer_info(file, file.tell())
                    print('end')

                except Exception:
                    LockFile.unlock(f'{self.db_directory}/table_{table_name}.bin')
                    raise

                LockFile.unlock(f'{self.db_directory}/table_{table_name}.bin')
                print('Inserted a row!')
                return

            else:
                file.write(encoded_line)
                print('Inserted a row!')
                return file.tell()

    def _search(self, table_name: str, criteria: dict, line_numbers=False, lock: bool = True):
        c_key = ''
        c_value = ''
        for key, value in criteria.items():
            c_key = key
            c_value = str(value)

        column_number = self.db_table_data[table_name][c_key][1]

        with open(f'{self.db_directory}/table_{table_name}.bin', 'rb') as file:
            if lock:
                LockFile.lock(f'{self.db_directory}/table_{table_name}.bin')

            file.seek(MAX_POINTER_CHARS * 2)

            try:
                for row in VeskoReaderWriter.read_table_file(file, self.META_DATA_LENGTH, column_number):
                    if row[0].decode() == c_value:
                        pos = file.tell()
                        file.seek(row[1] + row[2] + MAX_META_CHARS * 2, io.SEEK_SET)
                        raw_data = file.read(sum(row[3]))
                        data = codecs.decode(raw_data, 'hex')
                        list_data = VeskoReaderWriter.raw_data_to_list(row[3], data)
                        file.seek(pos)

                        if line_numbers:
                            yield row[1], row[2]

                        else:
                            yield list_data

            except Exception:
                LockFile.lock(f'{self.db_directory}/table_{table_name}.bin')
                raise

            if lock:
                LockFile.unlock(f'{self.db_directory}/table_{table_name}.bin')

    def select(self, table_name: str, criteria=None):
        assert table_name is not None, 'Argument "table_name" is required!'
        assert table_name in self.db_table_data, f'Table "{table_name}" not found!'

        if not criteria:
            with open(f'{self.db_directory}/table_{table_name}.bin', 'rb') as file:
                LockFile.lock(f'{self.db_directory}/table_{table_name}.bin')
                file.seek(MAX_POINTER_CHARS * 2)

                try:
                    for row in VeskoReaderWriter.read_table_file(file, self.META_DATA_LENGTH):
                        yield row[0]

                except Exception:
                    LockFile.lock(f'{self.db_directory}/table_{table_name}.bin')
                    raise

                LockFile.unlock(f'{self.db_directory}/table_{table_name}.bin')

        else:
            for row in self._search(table_name, criteria):
                yield row

    def delete(self, table_name: str, criteria: dict, lock: bool = True):
        assert table_name is not None, 'Argument "table_name" is required!'
        assert table_name in self.db_table_data, f'Table "{table_name}" not found!'

        with open(f'{self.db_directory}/table_{table_name}.bin', 'rb+') as file:
            for line in self._search(table_name, criteria, True, lock):
                file.seek(line[0] + line[1] + MAX_META_CHARS * 2 - DELETED_CHARS * 2 + 2)
                file.write(codecs.encode('-'.encode(), 'hex'))

                print('Deleted 1 row!')
                return True

    def update(self, table_name: str, criteria: dict, values: dict):
        assert table_name is not None, 'Argument "table_name" is required!'
        assert table_name in self.db_table_data, f'Table "{table_name}" not found!'
        assert values is not None, 'Argument "values" is required!'

        for row in self._search(table_name, criteria):
            row_dict = self.db_table_data[table_name].copy()

            for index, value in enumerate(row_dict):
                row_dict[value] = self.db_table_data[table_name][value][0].value(row[index])

            for key, value in values.items():
                row_dict[key] = self.db_table_data[table_name][key][0].value(value)

            position = self.insert(table_name, row_dict, False)

            if position:
                if self.delete(table_name, criteria, False):
                    with open(f'{self.db_directory}/table_{table_name}.bin', 'rb+') as file:
                        VeskoReaderWriter.write_pointer_info(file, position)
                    print('Updated 1 row!')


def test():
    try:
        engine = DbEngine()

        # engine.create_db('test1')
        engine.use_db('test1')

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
        # print(engine.db_table_data)

        tickets = {
            'ticket_id': DataType.INT,
            'name': DataType.TEXT,
            'reason': DataType.TEXT,
            'price': DataType.INT,
        }

        # engine.create_table('tickets', tickets)
        # print(engine.db_table_data)

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

        engine.insert('users', user)
        engine.insert('users', user1)
        engine.insert('users', user2)
        engine.insert('users', user3)
        engine.insert('users', user4)
        engine.insert('users', user5)

        # engine.use_db('test')

        # criteria = {
        #     'username': 'vesko',
        # }
        #
        # engine.select('users', criteria)

    except Exception as e:
        print(e)
        raise


def test_select():
    engine = DbEngine()

    engine.use_db('test1')

    criteria = {
        'user_id': 2,
    }

    for res in engine.select('users', criteria):
        print(res)

    # for row in engine.select('users'):
    #     print(row)

    # print(engine.select('users', criteria))
    # for row in engine.select('users', criteria):
    #     print(row)


def test_select_all():
    engine = DbEngine()

    engine.use_db('test1')

    for res in engine.select('users'):
        print(res)


def test_delete():
    engine = DbEngine()

    engine.use_db('test1')

    criteria = {
        'username': 'daniel',
    }

    engine.delete('users', criteria)


def test_update():
    engine = DbEngine()

    engine.use_db('test1')

    criteria = {
        'username': 'daniel',
    }

    values = {
        'username': 'vesko1',
        'password': 'oksev'
    }

    engine.update('users', criteria, values)


if __name__ == '__main__':
    test()
    # test_delete()
    # test_update()
    # test_select()
    test_select_all()

    # engine = DbEngine()
    #
    # engine.use_db('test1')
    #
    # print(engine.db_table_data)

    # with open(f'/home/veselin/Documents/databases/test1/table_users.bin', 'rb') as file:
    #     data = file.read()
    #     print(codecs.decode(data, 'hex'))

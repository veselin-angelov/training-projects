import codecs
import io
import os

from transaction import Transaction
from file_locker import FileLocker
from utilities import VeskoReaderWriter, MAX_META_CHARS, DELETED_CHARS, MAX_POINTER_CHARS, \
    MAX_CRITERION_CHARS, MAX_POSITION_CHARS, TRANSACTION_CHARS, MAX_PID_LENGTH


class DbEngine:
    DEFAULT_DB_DIR = '/home/veselin/Documents/databases/'
    META_DATA_LENGTH = 15
    CHUNK_SIZE = 10000
    MAX_ROWS_IN_MEMORY = 5000000
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
        # FileLocker.lock(self.db_meta_file_dir)

        try:
            self.db_meta_file = open(self.db_meta_file_dir, 'rb+')
            self.db_table_data = VeskoReaderWriter.read_meta_file(self.db_meta_file, self.META_DATA_LENGTH)

        except Exception:
            # FileLocker.unlock(self.db_meta_file_dir)
            raise

        # FileLocker.unlock(self.db_meta_file_dir)

        print(f'Using database {name}')

    def create_table(self, name: str, data: dict):
        assert name is not None, 'Argument "name" is required!'
        assert data is not None, 'Argument "data" is required!'

        try:
            open(f'{self.db_directory}/table_{name}.bin', 'x')

        except FileExistsError:
            print(f'Cannot create table "{name}". Already exists!')
            raise

        FileLocker.lock(f'{self.db_directory}/table_{name}.bin')

        try:
            table = open(f'{self.db_directory}/table_{name}.bin', 'wb')
            VeskoReaderWriter.write_pointer_info(table, MAX_POINTER_CHARS * 2)

        except Exception:
            FileLocker.unlock(f'{self.db_directory}/table_{name}.bin')
            raise

        FileLocker.unlock(f'{self.db_directory}/table_{name}.bin')

        FileLocker.lock(self.db_meta_file_dir)

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
            FileLocker.unlock(self.db_meta_file_dir)
            raise

        FileLocker.unlock(self.db_meta_file_dir)

    def __insert(self, file, table_name, encoded_line, criteria, update):
        position = VeskoReaderWriter.read_pointer_info(file)
        file.seek(position)

        file.write(encoded_line)

        if not update:
            VeskoReaderWriter.write_pointer_info(file, file.tell())

        file.flush()

        for criterion in criteria:
            self.insert_int_index(table_name, position, criterion)

    def insert(self, table_name: str, values: dict, update: bool = False):
        assert table_name is not None, 'Argument "table_name" is required!'
        assert values is not None, 'Argument "values" is required!'
        assert table_name in self.db_table_data, f'Table "{table_name}" not found!'
        assert len(self.db_table_data[table_name]) == len(values), \
            f'Expected {len(self.db_table_data[table_name])} values, got {len(values)}'

        try:
            table_data = self.db_table_data[table_name]
            insert_data = []
            criteria = []

            for column_name in table_data:
                assert column_name in values, f'Value for {column_name} is missing!'
                assert isinstance(values[column_name], table_data[column_name][0].value), \
                    f'Received {type(values[column_name])}, expected {table_data[column_name].value}!'

                if os.path.isfile(f'{self.db_directory}/index_{column_name}_{table_name}.bin'):
                    criteria.append({column_name: values[column_name]})

                insert_data.append(str(values[column_name]))

            encoded_line = VeskoReaderWriter.encode_line(insert_data, self.META_DATA_LENGTH)

            with open(f'{self.db_directory}/table_{table_name}.bin', 'rb+') as file:
                FileLocker.lock(f'{self.db_directory}/table_{table_name}.bin')
                self.__insert(file, table_name, encoded_line, criteria, update=update)
                print('Inserted a row!')
                return file.tell()

        except Exception:
            FileLocker.unlock(f'{self.db_directory}/table_{table_name}.bin')
            raise

        finally:
            FileLocker.unlock(f'{self.db_directory}/table_{table_name}.bin')

    def delete(self, table_name: str, criterion: dict, update: bool = False):
        assert table_name is not None, 'Argument "table_name" is required!'
        assert table_name in self.db_table_data, f'Table "{table_name}" not found!'

        try:
            c_key = None
            for key, value in criterion.items():
                c_key = key

            with open(f'{self.db_directory}/table_{table_name}.bin', 'rb+') as file:
                for row in self.search(table_name=table_name, criterion=criterion, line_numbers=True):
                    if not row.get('pid'):
                        file.seek(
                            row.get('position') +
                            row.get('meta_size') +
                            MAX_META_CHARS * 2 -
                            DELETED_CHARS * 2 -
                            TRANSACTION_CHARS * 2 -
                            MAX_PID_LENGTH * 2
                        )

                        FileLocker.lock(f'{self.db_directory}/table_{table_name}.bin')
                        file.write(codecs.encode('--'.encode(), 'hex'))
                        FileLocker.unlock(f'{self.db_directory}/table_{table_name}.bin')

                        if os.path.isfile(f'{self.db_directory}/index_{c_key}_{table_name}.bin'):
                            self.delete_from_int_index(table_name, criterion)

                        print('Deleted 1 row!')
                        if update:
                            return True

        except Exception:
            if FileLocker.check_lock(f'{self.db_directory}/table_{table_name}.bin'):
                FileLocker.unlock(f'{self.db_directory}/table_{table_name}.bin')
            raise

    def update(self, table_name: str, criterion: dict, values: dict):
        assert table_name is not None, 'Argument "table_name" is required!'
        assert table_name in self.db_table_data, f'Table "{table_name}" not found!'
        assert values is not None, 'Argument "values" is required!'

        try:
            file = open(f'{self.db_directory}/table_{table_name}.bin', 'rb')
            max_position = VeskoReaderWriter.read_pointer_info(file)

            for row in self.search(table_name, criterion):
                if row.get('position') > max_position:
                    break

                row_dict = self.db_table_data[table_name].copy()

                for value in row_dict:
                    row_dict[value] = self.db_table_data[table_name][value][0]\
                                        .value(row.get('list_data')[self.db_table_data[table_name][value][1]])

                for key, value in values.items():
                    row_dict[key] = self.db_table_data[table_name][key][0].value(value)

                position = self.insert(table_name, row_dict, update=True)

                if position and self.delete(table_name, criterion, update=True):
                    with open(f'{self.db_directory}/table_{table_name}.bin', 'rb+') as file:
                        FileLocker.lock(f'{self.db_directory}/table_{table_name}.bin')
                        VeskoReaderWriter.write_pointer_info(file, position)  # TODO revert delete if this fails
                        FileLocker.unlock(f'{self.db_directory}/table_{table_name}.bin')

                    print('Updated 1 row!')

        except Exception:
            FileLocker.unlock(f'{self.db_directory}/table_{table_name}.bin')
            raise

    def search(self, table_name: str, criterion: dict, line_numbers=False):
        assert table_name is not None, 'Argument "table_name" is required!'
        assert table_name in self.db_table_data, f'Table "{table_name}" not found!'
        assert criterion is not None, 'Argument "criterion" is required!'

        c_key = None
        c_value = None
        for key, value in criterion.items():
            c_key = key
            c_value = str(value)

        column_number = self.db_table_data[table_name][c_key][1]

        with open(f'{self.db_directory}/table_{table_name}.bin', 'rb') as file:
            file.seek(MAX_POINTER_CHARS * 2)
            for row in VeskoReaderWriter.read_table_file(file, self.META_DATA_LENGTH, column_number):
                if row.get('error') and row.get('data') == c_value:
                    raise row.get('error')

                elif row.get('data') == c_value:
                    if line_numbers:
                        yield {
                            'meta_size': row.get('meta_size'),
                            'position': row.get('position'),
                            'transaction_deleted': row.get('transaction_deleted'),
                            'pid': row.get('pid')
                        }

                    else:
                        pos = file.tell()
                        file.seek(row.get('position') + row.get('meta_size') + MAX_META_CHARS * 2, io.SEEK_SET)
                        raw_data = file.read(sum(row.get('data_len')))
                        data = codecs.decode(raw_data, 'hex').decode()
                        list_data = VeskoReaderWriter.raw_data_to_list(row.get('data_len'), data)
                        file.seek(pos)

                        yield {
                            'list_data': list_data,
                            'position': row.get('position')
                        }

    def select(self, table_name: str, criterion: dict = None):
        assert table_name is not None, 'Argument "table_name" is required!'
        assert table_name in self.db_table_data, f'Table "{table_name}" not found!'

        try:
            if not criterion:
                with open(f'{self.db_directory}/table_{table_name}.bin', 'rb') as file:
                    file.seek(MAX_POINTER_CHARS * 2)
                    for row in VeskoReaderWriter.read_table_file(file, self.META_DATA_LENGTH):
                        if row.get('error'):
                            raise row.get('error')

                        yield row.get('parsed_data')

            else:
                c_key = None
                for key, value in criterion.items():
                    c_key = key

                if os.path.isfile(f'{self.db_directory}/index_{c_key}_{table_name}.bin'):
                    with open(f'{self.db_directory}/table_{table_name}.bin', 'rb') as file:
                        for offset in self.search_in_int_index(table_name, criterion):  # TODO search in transaction with index
                            result = VeskoReaderWriter.read_from_given_offset(file, offset, self.META_DATA_LENGTH)

                            if result is not None:
                                yield result

                else:
                    for row in self.search(table_name, criterion):
                        yield row.get('list_data')

        except Exception:
            raise

    def create_int_index(self, table_name: str, criterion: str):
        assert table_name is not None, 'Argument "table_name" is required!'
        assert table_name in self.db_table_data, f'Table "{table_name}" not found!'
        assert criterion is not None, 'Argument "criterion" is required!'

        try:
            open(f'{self.db_directory}/index_{criterion}_{table_name}.bin', 'x')
            open(f'{self.db_directory}/index_data_{criterion}_{table_name}.bin', 'x')
        except FileExistsError:
            print(f'Cannot create {criterion} index on table "{table_name}". Already exists!')
            raise

        data_length = MAX_CRITERION_CHARS * 2 + MAX_POSITION_CHARS * 4
        column_number = self.db_table_data[table_name][criterion][1]
        column_type = self.db_table_data[table_name][criterion][0]
        unique_column_data = set()
        rows = 0

        with open(f'{self.db_directory}/table_{table_name}.bin', 'rb') as table:
            table.seek(MAX_POINTER_CHARS * 2)

            for row in VeskoReaderWriter.read_table_file(table, self.META_DATA_LENGTH, column_number):
                row_data = column_type.value(row[0].decode())
                unique_column_data.add(row_data)

                rows += 1

                if rows > self.MAX_ROWS_IN_MEMORY:
                    pass

        values_count = len(unique_column_data)
        max_value = max(unique_column_data)

        index_range = max_value

        if max_value - values_count > 500000:
            index_range = values_count + 500000

        unique_column_data_exclusive = [i for i in unique_column_data if i > index_range]
        unique_column_data.clear()

        index_seq = open(f'{self.db_directory}/index_{criterion}_{table_name}.bin', 'rb+')
        for i in range(index_range + 100000):
            blank_space_criterion = MAX_CRITERION_CHARS - len(str(i))
            data = f'{i}{" " * blank_space_criterion}{" " * MAX_POSITION_CHARS}{" " * MAX_POSITION_CHARS}'

            index_seq.write(codecs.encode(data.encode(), 'hex'))

        for element in unique_column_data_exclusive:
            blank_space_criterion = MAX_CRITERION_CHARS - len(str(element))
            data = f'{element}{" " * blank_space_criterion}{" " * MAX_POSITION_CHARS}{" " * MAX_POSITION_CHARS}'

            index_seq.write(codecs.encode(data.encode(), 'hex'))

        unique_column_data_exclusive.clear()

        index_seq.seek(io.SEEK_SET)

        index_data = open(f'{self.db_directory}/index_data_{criterion}_{table_name}.bin', 'rb+')

        with open(f'{self.db_directory}/table_{table_name}.bin', 'rb') as table:
            table.seek(MAX_POINTER_CHARS * 2)

            for row in VeskoReaderWriter.read_table_file(table, self.META_DATA_LENGTH, column_number):
                row_data = column_type.value(row[0].decode())
                position = row[1]

                index_seq.seek(row_data * data_length)

                data = VeskoReaderWriter.read_index_file(index_seq)

                if data[0] == row_data:
                    VeskoReaderWriter.write_index_data_file(index_seq, index_data, position, data)

                else:
                    index_seq_size = os.stat(f'{self.db_directory}/index_{criterion}_{table_name}.bin').st_size
                    result = VeskoReaderWriter.binary_search(index_seq, index_seq_size, row_data, data_length)
                    VeskoReaderWriter.write_index_data_file(index_seq, index_data, position, result)

        print('Created index!')

    def delete_int_index(self, table_name: str, criterion: str):
        try:
            os.remove(f'{self.db_directory}/index_{criterion}_{table_name}.bin')
            os.remove(f'{self.db_directory}/index_data_{criterion}_{table_name}.bin')

        except Exception as e:
            print(e)
            raise

    def search_in_int_index(self, table_name: str, criterion: dict):
        assert table_name is not None, 'Argument "index_name" is required!'
        assert criterion is not None, 'Argument "criterion" is required!'

        data_length = MAX_CRITERION_CHARS * 2 + MAX_POSITION_CHARS * 4

        c_key = None
        c_value = None
        for key, value in criterion.items():
            c_key = key
            c_value = value

        assert os.path.isfile(f'{self.db_directory}/index_{c_key}_{table_name}.bin'), \
            f'Index on column "{c_key}" in table "{table_name}" does not exist!'

        try:
            index_seq = open(f'{self.db_directory}/index_{c_key}_{table_name}.bin', 'rb')
            index_seq.seek(c_value * data_length)

            index_seq_data = VeskoReaderWriter.read_index_file(index_seq)

            offset = index_seq_data[1]

            if index_seq_data[0] != c_value:
                index_seq_size = os.stat(f'{self.db_directory}/index_{c_key}_{table_name}.bin').st_size
                result = VeskoReaderWriter.binary_search(index_seq, index_seq_size, c_value, data_length)
                if result[0]:
                    offset = result[1]

            index_data = open(f'{self.db_directory}/index_data_{c_key}_{table_name}.bin', 'rb')

            if offset is None:
                print('Record not found!')
                return

            index_data.seek(offset, io.SEEK_SET)

            while True:
                index_data_data = VeskoReaderWriter.read_index_data_file(index_data)

                yield index_data_data[0]

                if not index_data_data[1]:
                    break

                index_data.seek(index_data_data[1])

        except Exception as e:
            print(e)
            raise

    def insert_int_index(self, table_name: str, position: int, criterion: dict):
        assert table_name is not None, 'Argument "index_name" is required!'
        assert position is not None, 'Argument "position" is required!'
        assert criterion is not None, 'Argument "criterion" is required!'

        data_length = MAX_CRITERION_CHARS * 2 + MAX_POSITION_CHARS * 4

        c_key = None
        c_value = None
        for key, value in criterion.items():
            c_key = key
            c_value = value

        index_seq = open(f'{self.db_directory}/index_{c_key}_{table_name}.bin', 'rb+')
        index_data = open(f'{self.db_directory}/index_data_{c_key}_{table_name}.bin', 'rb+')

        index_seq.seek(c_value * data_length)

        data = VeskoReaderWriter.read_index_file(index_seq)

        if data[0] == c_value:
            VeskoReaderWriter.write_index_data_file(index_seq, index_data, position, data)

        else:
            index_seq_size = os.stat(f'{self.db_directory}/index_{c_key}_{table_name}.bin').st_size
            result = VeskoReaderWriter.binary_search(index_seq, index_seq_size, c_value, data_length)

            if result[0]:  # index key
                VeskoReaderWriter.write_index_data_file(index_seq, index_data, position, result)

            else:
                if result[1] == 1:  # add to the end of index file
                    index_seq.seek(0, io.SEEK_END)
                    VeskoReaderWriter.write_index_seq_file(index_seq, index_data, c_key, c_value, position, data_length,
                                                           self.db_directory, table_name)

                else:
                    index_seq.seek(index_seq.tell() - data_length)

                    flag = False
                    old_row = None

                    while True:
                        row = VeskoReaderWriter.read_index_file(index_seq)

                        if not row[0]:
                            break

                        if c_value < row[0] and not flag:
                            index_seq.seek(index_seq.tell() - data_length)
                            VeskoReaderWriter.write_index_seq_file(index_seq, index_data, c_key, c_value, position,
                                                                   data_length, self.db_directory, table_name)
                            old_row = row
                            flag = True

                        elif flag:
                            blank_space_criterion = MAX_CRITERION_CHARS - len(str(old_row[0]))
                            blank_space_first = MAX_POSITION_CHARS - len(str(old_row[1]))
                            blank_space_last = MAX_POSITION_CHARS - len(str(old_row[2]))
                            data = f'{old_row[0]}{" " * blank_space_criterion}' \
                                   f'{old_row[1]}{" " * blank_space_first}' \
                                   f'{old_row[2]}{" " * blank_space_last}'
                            index_seq.seek(index_seq.tell() - data_length, io.SEEK_SET)
                            index_seq.write(codecs.encode(data.encode(), 'hex'))
                            index_seq.flush()
                            old_row = row

    def delete_from_int_index(self, table_name: str, criterion: dict):
        assert table_name is not None, 'Argument "index_name" is required!'
        assert criterion is not None, 'Argument "criterion" is required!'

        data_length = MAX_CRITERION_CHARS * 2 + MAX_POSITION_CHARS * 4

        c_key = None
        c_value = None
        for key, value in criterion.items():
            c_key = key
            c_value = value

        try:
            index_seq = open(f'{self.db_directory}/index_{c_key}_{table_name}.bin', 'rb+')
            index_seq.seek(c_value * data_length)

            index_seq_data = VeskoReaderWriter.read_index_file(index_seq)

            if index_seq_data[0] != c_value:
                index_seq_size = os.stat(f'{self.db_directory}/index_{c_key}_{table_name}.bin').st_size
                result = VeskoReaderWriter.binary_search(index_seq, index_seq_size, c_value, data_length)
                if result[0]:
                    c_value = result[1]

            index_seq.seek(c_value * data_length + MAX_CRITERION_CHARS * 2)
            write_data = f'{" " * MAX_POSITION_CHARS * 2}'
            index_seq.write(codecs.encode(write_data.encode(), 'hex'))

        except Exception as e:
            print(e)
            raise

    def begin_transaction(self):
        return Transaction(self)

    # def read_index(self):
    #     with open(f'{self.db_directory}/index_id_table.bin', 'rb') as index_seq:
    #         while True:
    #             data = VeskoReaderWriter.read_index_file(index_seq)
    #             print(data)
    #             if data[0] is None:
    #                 break

    # def read_file_test(self):
    #     with open(f'{self.db_directory}/index_data_id_table.bin', 'rb') as index_data:
    #         data = index_data.read()
    #         data = codecs.decode(data, 'hex')
    #         print(data)

import codecs
import io
import os
import time
from time import sleep

from utilities import DataType, LockFile, VeskoReaderWriter, MAX_META_CHARS, DELETED_CHARS, MAX_POINTER_CHARS, \
    MAX_CRITERIA_CHARS, MAX_POSITION_CHARS


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
            position = VeskoReaderWriter.read_pointer_info(file)
            file.seek(position)

            if lock:
                LockFile.lock(f'{self.db_directory}/table_{table_name}.bin')

                try:
                    file.write(encoded_line)
                    self.insert_index(table_name, position, criteria)  # TODO criteria is a part of values
                    VeskoReaderWriter.write_pointer_info(file, file.tell())

                except Exception:
                    LockFile.unlock(f'{self.db_directory}/table_{table_name}.bin')
                    raise

                LockFile.unlock(f'{self.db_directory}/table_{table_name}.bin')
                print('Inserted a row!')
                return

            else:
                file.write(encoded_line)
                self.insert_index(table_name, position, criteria)
                VeskoReaderWriter.write_pointer_info(file, file.tell())
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
                        if line_numbers:
                            yield row[1], row[2]
                        else:
                            pos = file.tell()
                            file.seek(row[1] + row[2] + MAX_META_CHARS * 2, io.SEEK_SET)
                            raw_data = file.read(sum(row[3]))
                            data = codecs.decode(raw_data, 'hex')
                            list_data = VeskoReaderWriter.raw_data_to_list(row[3], data)
                            file.seek(pos)

                            yield list_data

            except Exception:
                LockFile.unlock(f'{self.db_directory}/table_{table_name}.bin')
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
                    LockFile.unlock(f'{self.db_directory}/table_{table_name}.bin')
                    raise

                LockFile.unlock(f'{self.db_directory}/table_{table_name}.bin')

        else:
            c_key = ''
            for key, value in criteria.items():
                c_key = key

            if os.path.isfile(f'{self.db_directory}/index_{c_key}_{table_name}.bin'):
                with open(f'{self.db_directory}/table_{table_name}.bin', 'rb') as file:
                    LockFile.lock(f'{self.db_directory}/table_{table_name}.bin')

                    try:
                        for offset in self.search_in_index(table_name, criteria):
                            yield VeskoReaderWriter.read_from_given_offset(file, offset, self.META_DATA_LENGTH)

                    except Exception:
                        LockFile.unlock(f'{self.db_directory}/table_{table_name}.bin')
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

    def create_index(self, table_name: str, criteria: str):
        assert table_name is not None, 'Argument "table_name" is required!'
        assert table_name in self.db_table_data, f'Table "{table_name}" not found!'
        assert criteria is not None, 'Argument "criteria" is required!'

        try:
            open(f'{self.db_directory}/index_{criteria}_{table_name}.bin', 'x')
            open(f'{self.db_directory}/index_data_{criteria}_{table_name}.bin', 'x')
        except FileExistsError:
            print(f'Cannot create {criteria} index on table "{table_name}". Already exists!')
            raise

        data_length = MAX_CRITERIA_CHARS * 2 + MAX_POSITION_CHARS * 4
        column_number = self.db_table_data[table_name][criteria][1]
        column_type = self.db_table_data[table_name][criteria][0]
        unique_column_data = set()
        rows = 0

        with open(f'{self.db_directory}/table_{table_name}.bin', 'rb') as table:
            table.seek(MAX_POINTER_CHARS * 2)

            for row in VeskoReaderWriter.read_table_file(table, self.META_DATA_LENGTH, column_number):
                row_data = column_type.value(row[0].decode())
                unique_column_data.add(row_data)

                rows += 1

                if rows > self.MAX_ROWS_IN_MEMORY:
                    pass  # TODO

        values_count = len(unique_column_data)
        max_value = max(unique_column_data)
        unique_column_data.clear()

        index_range = max_value

        if max_value - values_count > 500000:
            index_range = values_count + 500000

        index_seq = open(f'{self.db_directory}/index_{criteria}_{table_name}.bin', 'rb+')
        for i in range(index_range + 100000):
            blank_space_criteria = MAX_CRITERIA_CHARS - len(str(i))
            data = f'{i}{" " * blank_space_criteria}{" " * MAX_POSITION_CHARS}{" " * MAX_POSITION_CHARS}'

            index_seq.write(codecs.encode(data.encode(), 'hex'))

        index_seq.seek(io.SEEK_SET)

        index_data = open(f'{self.db_directory}/index_data_{criteria}_{table_name}.bin', 'rb+')

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
                    pass  # TODO binary search

        print('Created index!')

    def search_in_index(self, table_name: str, criteria: dict):
        assert table_name is not None, 'Argument "index_name" is required!'
        assert criteria is not None, 'Argument "criteria" is required!'

        data_length = MAX_CRITERIA_CHARS * 2 + MAX_POSITION_CHARS * 4

        c_key = ''
        c_value = ''
        for key, value in criteria.items():
            c_key = key
            c_value = value

        try:
            index_seq = open(f'{self.db_directory}/index_{c_key}_{table_name}.bin', 'rb')
            index_seq.seek(c_value * data_length)

            index_seq_data = VeskoReaderWriter.read_index_file(index_seq)

            if index_seq_data[0] != c_value:
                return  # TODO binary search

            index_data = open(f'{self.db_directory}/index_data_{c_key}_{table_name}.bin', 'rb')

            index_data.seek(index_seq_data[1], io.SEEK_SET)

            with open(f'{self.db_directory}/table_{table_name}.bin', 'rb') as table:
                while True:
                    index_data_data = VeskoReaderWriter.read_index_data_file(index_data)
                    # print(VeskoReaderWriter.read_from_given_offset(table, index_data_data[0], self.META_DATA_LENGTH))
                    yield index_data_data[0]

                    if not index_data_data[1]:
                        break

                    index_data.seek(index_data_data[1])

        except Exception as e:
            print(e)
            raise

    # def read_index(self):
    #     with open(f'{self.db_directory}/index_id_table.bin', 'rb') as index_seq:
    #         while True:
    #             data = VeskoReaderWriter.read_index_file(index_seq)
    #             print(data)
    #             if data[0] is None:
    #                 break
    #
    # def read_file_test(self):
    #     with open(f'{self.db_directory}/index_data_id_table.bin', 'rb') as index_data:
    #         data = index_data.read()
    #         data = codecs.decode(data, 'hex')
    #         print(data)

    def insert_index(self, table_name: str, position: int, criteria: dict):
        assert table_name is not None, 'Argument "index_name" is required!'
        assert criteria is not None, 'Argument "criteria" is required!'

        data_length = MAX_CRITERIA_CHARS * 2 + MAX_POSITION_CHARS * 4

        c_key = ''
        c_value = ''
        for key, value in criteria.items():
            c_key = key
            c_value = value

        index_seq = open(f'{self.db_directory}/index_{c_key}_{table_name}.bin', 'rb+')
        index_data = open(f'{self.db_directory}/index_data_{c_key}_{table_name}.bin', 'rb+')

        data = VeskoReaderWriter.read_index_file(index_seq)

        index_seq.seek(c_value * data_length)

        if data[0] == c_value:
            VeskoReaderWriter.write_index_data_file(index_seq, index_data, position, data)

        else:
            pass  # TODO binary search

    def update_index(self):  # delete the row, just add the new row to the index table
        pass

    def delete_index(self, table_name: str, criteria: dict):
        assert table_name is not None, 'Argument "index_name" is required!'
        assert criteria is not None, 'Argument "criteria" is required!'

        data_length = MAX_CRITERIA_CHARS * 2 + MAX_POSITION_CHARS * 4

        c_key = ''
        c_value = ''
        for key, value in criteria.items():
            c_key = key
            c_value = value

        try:
            index_seq = open(f'{self.db_directory}/index_{c_key}_{table_name}.bin', 'rb')
            index_seq.seek(c_value * data_length)

            index_seq_data = VeskoReaderWriter.read_index_file(index_seq)

            if index_seq_data[0] != c_value:
                return  # TODO binary search

            index_seq.seek(c_value * data_length + MAX_CRITERIA_CHARS * 2)
            write_data = f'{" " * MAX_POSITION_CHARS * 2}'
            index_seq.write(codecs.encode(write_data, 'hex'))

        except Exception as e:
            print(e)
            raise

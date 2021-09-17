import codecs
import io
import os
import traceback

from file_locker import FileLocker
from utilities import VeskoReaderWriter, DELETED_CHARS, TRANSACTION_CHARS, MAX_PID_LENGTH, MAX_META_CHARS


class Transaction(object):
    altered_rows = dict()
    finished = False

    def __init__(self, engine_instance):
        self.engine = engine_instance

    def __enter__(self):  # start transaction, return engine object
        return self

    def __exit__(self, exc_type, exc_value, exc_traceback):
        if exc_type is not None:
            traceback.print_exception(exc_type, exc_value, exc_traceback)
            return False

        if not self.finished:
            self.rollback()

    def commit(self):
        self.__commit_or_rollback(commit=True)
        self.finished = True
        print('Committed!')
        return

    def rollback(self):
        self.__commit_or_rollback(commit=False)
        self.finished = True
        print('Rolled back!')
        return

    def __commit_or_rollback(self, commit: bool):
        for table_name, positions in self.altered_rows.items():
            with open(f'{self.engine.db_directory}/table_{table_name}.bin', 'rb+') as file:
                while positions:
                    position = positions.pop()
                    file.seek(position)

                    data = VeskoReaderWriter.read_table_meta_data(file)

                    if not data:
                        raise

                    if data.get('pid') == os.getpid():
                        file.seek(-(DELETED_CHARS * 2 + TRANSACTION_CHARS * 2 + MAX_PID_LENGTH * 2), io.SEEK_CUR)
                        if data.get('deleted') == b'-' and data.get('transaction_deleted') == b'+':
                            file.write(codecs.encode(f'{"++" if commit else "--"}{" " * MAX_PID_LENGTH}'.encode(), 'hex'))

                        elif data.get('deleted') == b'+' and data.get('transaction_deleted') == b'-':
                            file.write(codecs.encode(f'{"--" if commit else "++"}{" " * MAX_PID_LENGTH}'.encode(), 'hex'))

    def insert(self, table_name: str, values: dict):
        assert table_name is not None, 'Argument "table_name" is required!'
        assert values is not None, 'Argument "values" is required!'
        assert table_name in self.engine.db_table_data, f'Table "{table_name}" not found!'
        assert len(self.engine.db_table_data[table_name]) == len(values), \
            f'Expected {len(self.engine.db_table_data[table_name])} values, got {len(values)}'

        table_data = self.engine.db_table_data[table_name]
        insert_data = []
        criteria = []

        for column_name in table_data:
            assert column_name in values, f'Value for {column_name} is missing!'
            assert isinstance(values[column_name], table_data[column_name][0].value), \
                f'Received {type(values[column_name])}, expected {table_data[column_name].value}!'

            if os.path.isfile(f'{self.engine.db_directory}/index_{column_name}_{table_name}.bin'):
                criteria.append({column_name: values[column_name]})

            insert_data.append(str(values[column_name]))

        encoded_line = VeskoReaderWriter.encode_line(
            insert_data,
            self.engine.META_DATA_LENGTH,
            deleted='-',
            pid=os.getpid()
        )

        with open(f'{self.engine.db_directory}/table_{table_name}.bin', 'rb+') as file:
            position = VeskoReaderWriter.read_pointer_info(file)
            file.seek(position)

            file.write(encoded_line)
            VeskoReaderWriter.write_pointer_info(file, file.tell())
            file.flush()

            if table_name in self.altered_rows.keys():
                self.altered_rows[table_name].append(position)

            else:
                self.altered_rows[table_name] = [position]

            print('Inserted a row!')
            # return criteria  # TODO create index
            return file.tell()  # TODO to be passed to index

    def delete(self, table_name: str, criterion: dict,):  # TODO delete in transaction, try - except
        assert table_name is not None, 'Argument "table_name" is required!'
        assert table_name in self.engine.db_table_data, f'Table "{table_name}" not found!'

        # c_key = None
        # for key, value in criterion.items():
        #     c_key = key

        with open(f'{self.engine.db_directory}/table_{table_name}.bin', 'rb+') as file:
            for row in self.engine.search(table_name, criterion, line_numbers=True):
                if not row.get('pid'):
                    if table_name in self.altered_rows.keys():
                        self.altered_rows[table_name].append(row.get('position'))

                    else:
                        self.altered_rows[table_name] = [row.get('position')]

                    file.seek(row.get('position') + row.get('meta_size') +
                              MAX_META_CHARS * 2 - TRANSACTION_CHARS * 2 - MAX_PID_LENGTH * 2)

                    pid_blank_space = MAX_PID_LENGTH - len(str(os.getpid()))
                    file.write(codecs.encode(f'-{os.getpid()}{" " * pid_blank_space}'.encode(), 'hex'))

                    # if os.path.isfile(f'{self.engine.db_directory}/index_{c_key}_{table_name}.bin'):  # TODO delete from index
                    #     self.engine.delete_from_int_index(table_name, criterion)

                    print('Deleted 1 row!')

    def update(self, table_name: str, criterion: dict, values: dict):  # TODO update in transaction
        assert table_name is not None, 'Argument "table_name" is required!'
        assert table_name in self.engine.db_table_data, f'Table "{table_name}" not found!'
        assert values is not None, 'Argument "values" is required!'

        try:
            file = open(f'{self.engine.db_directory}/table_{table_name}.bin', 'rb')
            max_position = VeskoReaderWriter.read_pointer_info(file)

            for row in self.engine.search(table_name, criterion):
                if row.get('position') > max_position:
                    break

                row_dict = self.engine.db_table_data[table_name].copy()

                for value in row_dict:
                    row_dict[value] = self.engine.db_table_data[table_name][value][0] \
                        .value(row.get('list_data')[self.engine.db_table_data[table_name][value][1]])

                for key, value in values.items():
                    row_dict[key] = self.engine.db_table_data[table_name][key][0].value(value)

                position = self.insert(table_name, row_dict, update=True)

                if position and self.delete(table_name, criterion, update=True):
                    with open(f'{self.engine.db_directory}/table_{table_name}.bin', 'rb+') as file:
                        FileLocker.lock(f'{self.engine.db_directory}/table_{table_name}.bin')
                        VeskoReaderWriter.write_pointer_info(file, position)  # TODO revert delete
                        FileLocker.unlock(f'{self.engine.db_directory}/table_{table_name}.bin')

                    print('Updated 1 row!')

        except Exception:
            FileLocker.unlock(f'{self.engine.db_directory}/table_{table_name}.bin')
            raise

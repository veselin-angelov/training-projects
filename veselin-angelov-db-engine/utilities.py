import codecs
import io
import os
from enum import Enum

MAX_META_CHARS = 6  # len of all meta data
MAX_POINTER_CHARS = 20
MAX_CRITERION_CHARS = 10
MAX_POSITION_CHARS = 12
DELETED_CHARS = 1
TRANSACTION_CHARS = 1
MAX_PID_LENGTH = 7


class DataType(Enum):
    INT = int
    TEXT = str


class TableInTransactionException(Exception):
    pass


class RowInTransactionException(Exception):
    pass


class VeskoReaderWriter:

    @staticmethod
    def encode_line(values: list, meta_length: int, pid: int = None, deleted: str = "+", transaction_deleted: str = "+"):
        assert values is not None, 'Argument "values" is required!'
        assert meta_length is not None, 'Argument "meta_length" is required!'

        values_len = []

        meta_data_size = len(values) * meta_length * 2 + DELETED_CHARS * 2 + TRANSACTION_CHARS * 2 + MAX_PID_LENGTH * 2
        meta_data_size_blank_space = MAX_META_CHARS - len(str(meta_data_size))
        data = f'{meta_data_size}{" " * meta_data_size_blank_space}'

        if pid:
            pid_blank_space = MAX_PID_LENGTH - len(str(pid))
        else:
            pid_blank_space = MAX_PID_LENGTH

        for value in values:
            value_len = len(value) * 2  # HEX len is twice the normal
            value_len_decimals = len(str(value_len))

            blank_space = meta_length - value_len_decimals

            values_len.append(f'{value_len}{" " * blank_space}')

        data += f'{"".join(values_len)}' \
                f'{deleted}' \
                f'{transaction_deleted}' \
                f'{pid if pid else ""}' \
                f'{" " * pid_blank_space}' \
                f'{"".join(values)}'

        data = data.encode()
        return codecs.encode(data, 'hex')

    @staticmethod
    def raw_data_to_list(data_len: list, data: str):
        assert data_len is not None, 'Argument "data_len" is required!'
        assert data is not None, 'Argument "data" is required!'

        result = []
        prev = 0

        for column_size in data_len:
            index = int(column_size / 2)
            value = data[prev:prev + index]
            result.append(value)
            prev += index

        return result

    @staticmethod
    def read_table_meta_data(f):
        assert f is not None, 'Argument "f" is required!'

        meta_size = f.read(MAX_META_CHARS * 2)
        meta_size = codecs.decode(meta_size, 'hex')

        if meta_size == b'':
            return None

        meta_size = int(meta_size)

        meta = f.read(meta_size)
        meta_readable = codecs.decode(meta, 'hex')
        pid = meta_readable[-MAX_PID_LENGTH:]
        transaction_deleted = meta_readable[-(MAX_PID_LENGTH + TRANSACTION_CHARS):-MAX_PID_LENGTH]
        deleted = meta_readable[
                  -(MAX_PID_LENGTH + TRANSACTION_CHARS + DELETED_CHARS):-(MAX_PID_LENGTH + TRANSACTION_CHARS)]

        pid = int(pid) if pid.strip() else None

        return {
            'meta_size': meta_size,
            'meta_readable': meta_readable,
            'deleted': deleted,
            'transaction_deleted': transaction_deleted,
            'pid': pid
        }

    @staticmethod
    def read_from_given_offset(f, offset: int, meta_length: int):  # TODO check the function
        assert f is not None, 'Argument "f" is required!'
        assert offset is not None, 'Argument "offset" is required!'
        assert meta_length is not None, 'Argument "meta_length" is required!'

        f.seek(offset)
        meta_data = VeskoReaderWriter.read_table_meta_data(f)

        if not meta_data:
            return None

        data_len = []
        for start in range(0, len(meta_data.get('meta_readable')) - (MAX_PID_LENGTH + TRANSACTION_CHARS + DELETED_CHARS), meta_length):
            data_len.append(int(meta_data.get('meta_readable')[start:start + meta_length]))

        if meta_data.get('transaction_deleted') == b'+' or meta_data.get('deleted') == b'+':
            if meta_data.get('pid') is not None and meta_data.get('pid') != os.getpid():
                raise RowInTransactionException

            else:
                data = f.read(sum(data_len))
                return VeskoReaderWriter.raw_data_to_list(data_len, codecs.decode(data, 'hex').decode())

    @staticmethod
    def __make_response(meta_data, data, data_len, position):
        data = codecs.decode(data, 'hex').decode()

        if meta_data.get('pid') is not None and meta_data.get('pid') != os.getpid():
            return {
                'data': data,
                'error': RowInTransactionException
            }

        else:
            return {
                'data': data,
                'data_len': data_len,
                'position': position,
                'meta_size': meta_data.get('meta_size'),
                'transaction_deleted': meta_data.get('transaction_deleted'),
                'pid': meta_data.get('pid')
            }

    @staticmethod
    def read_file(f, meta_length: int, column_number: int = None, read_table_data: bool = False):
        assert f is not None, 'Argument "f" is required!'
        assert meta_length is not None, 'Argument "meta_length" is required!'

        while True:
            position = f.tell()

            if read_table_data and position == VeskoReaderWriter.read_pointer_info(f):
                break

            meta_data = VeskoReaderWriter.read_table_meta_data(f)

            if not meta_data:
                break

            data_len = []
            for start in range(0, len(meta_data.get('meta_readable')) - (MAX_PID_LENGTH + TRANSACTION_CHARS + DELETED_CHARS), meta_length):
                data_len.append(int(meta_data.get('meta_readable')[start:start + meta_length]))

            if meta_data.get('transaction_deleted') == b'+' or meta_data.get('deleted') == b'+':
                if column_number is not None:
                    for index, column_len in enumerate(data_len):
                        if index == column_number:
                            data = f.read(column_len)
                            yield VeskoReaderWriter.__make_response(meta_data, data, data_len, position)

                        else:
                            f.seek(column_len, io.SEEK_CUR)

                else:
                    data = f.read(sum(data_len))
                    yield VeskoReaderWriter.__make_response(meta_data, data, data_len, position)

            else:
                f.seek(sum(data_len), io.SEEK_CUR)

    @staticmethod
    def read_table_file(f, meta_length: int, column_number: int = None):
        assert f is not None, 'Argument "f" is required!'
        assert meta_length is not None, 'Argument "meta_length" is required!'

        for row in VeskoReaderWriter.read_file(f, meta_length, column_number, True):

            if row.get('error'):
                yield row
                continue

            if column_number is not None:
                yield {
                    'data': row.get('data'),
                    'data_len': row.get('data_len'),
                    'position': row.get('position'),
                    'meta_size': row.get('meta_size'),
                    'transaction_deleted': row.get('transaction_deleted'),
                    'pid': row.get('pid')
                }

            else:
                yield {
                    'parsed_data': VeskoReaderWriter.raw_data_to_list(row.get('data_len'), row.get('data')),
                    'position': row.get('position'),
                    'meta_size': row.get('meta_size')
                }

    @staticmethod
    def read_meta_file(f, meta_length: int):
        assert f is not None, 'Argument "f" is required!'
        assert meta_length is not None, 'Argument "meta_length" is required!'

        tables = dict()

        for row in VeskoReaderWriter.read_file(f, meta_length):
            prev = 0
            position = 0
            table_name = ''
            for count, column_size in enumerate(row.get('data_len')):
                if count % 2 != 0 or prev == 0:
                    index = int(column_size / 2)
                    name = row.get('data')[prev:prev + index]
                    prev += index

                    if prev - index == 0:
                        table_name = name
                        tables[table_name] = {}

                    else:
                        index1 = int(row.get('data_len')[count + 1] / 2)
                        value = row.get('data')[prev:prev + index1]
                        tables[table_name][name] = getattr(DataType, value), position
                        prev += index1
                        position += 1

        return tables

    @staticmethod
    def read_pointer_info(f):
        assert f is not None, 'Argument "f" is required!'

        pos = f.tell()
        f.seek(0)
        data = f.read(MAX_POINTER_CHARS * 2)
        data = codecs.decode(data, 'hex')
        f.seek(pos)

        return int(data)

    @staticmethod
    def write_pointer_info(f, position: int):
        assert f is not None, 'Argument "f" is required!'
        assert position is not None, 'Argument "position" is required!'

        blank_space = MAX_POINTER_CHARS - len(str(position))
        data = f'{position}{" " * blank_space}'
        data = data.encode()

        f.seek(0)
        f.write(codecs.encode(data, 'hex'))

    @staticmethod
    def read_index_file(f):  # TODO add transaction delete and delete flag to index
        assert f is not None, 'Argument "f" is required!'

        data = f.read(MAX_CRITERION_CHARS * 2 + MAX_POSITION_CHARS * 4)
        data = codecs.decode(data, 'hex')

        index_data = data[:MAX_CRITERION_CHARS]
        first_element = data[MAX_CRITERION_CHARS:MAX_CRITERION_CHARS + MAX_POSITION_CHARS]
        last_element = data[MAX_CRITERION_CHARS + MAX_POSITION_CHARS:]

        index_data = int(index_data) if index_data.strip() else None
        first_element = int(first_element) if first_element.strip() else None
        last_element = int(last_element) if last_element.strip() else None

        return index_data, first_element, last_element

    @staticmethod
    def read_index_data_file(f):
        assert f is not None, 'Argument "f" is required!'

        data = f.read(MAX_POSITION_CHARS * 4)
        data = codecs.decode(data, 'hex')

        data_pointer = data[:MAX_POSITION_CHARS]
        next_element = data[MAX_POSITION_CHARS:]

        data_pointer = int(data_pointer) if data_pointer.strip() else None
        next_element = int(next_element) if next_element.strip() else None

        return data_pointer, next_element

    @staticmethod
    def write_index_data_file(index_seq, index_data, position: int, data: list):
        assert index_seq is not None, 'Argument "index_seq" is required!'
        assert index_data is not None, 'Argument "index_data" is required!'
        assert position is not None, 'Argument "position" is required!'
        assert data is not None, 'Argument "data" is required!'

        index_data.seek(0, io.SEEK_END)
        pointer = index_data.tell()
        position_blank_space = MAX_POSITION_CHARS - len(str(position))
        write_index_data = f'{position}{" " * position_blank_space}{" " * MAX_POSITION_CHARS}'
        index_data.write(codecs.encode(write_index_data.encode(), 'hex'))

        if data and data[1] and data[2]:
            pointer_blank_space = MAX_POSITION_CHARS - len(str(pointer))
            latest_index_data = f'{pointer}{" " * pointer_blank_space}'
            index_data.seek(data[2] + MAX_POSITION_CHARS * 2, io.SEEK_SET)
            index_data.write(codecs.encode(latest_index_data.encode(), 'hex'))

            index_seq.seek(index_seq.tell() - MAX_POSITION_CHARS * 2)
            index_seq.write(codecs.encode(latest_index_data.encode(), 'hex'))

        else:
            pointer_blank_space = MAX_POSITION_CHARS - len(str(pointer))
            index_seq.seek(index_seq.tell() - MAX_POSITION_CHARS * 4)
            write_index_seq = f'{pointer}{" " * pointer_blank_space}{pointer}{" " * pointer_blank_space}'
            index_seq.write(codecs.encode(write_index_seq.encode(), 'hex'))

    @staticmethod
    def write_index_seq_file(index_seq, index_data, key, value, position, data_length, db_dir, table_name):
        assert index_seq is not None, 'Argument "index_seq" is required!'
        assert index_data is not None, 'Argument "index_data" is required!'
        assert position is not None, 'Argument "position" is required!'
        assert key is not None, 'Argument "key" is required!'
        assert value is not None, 'Argument "value" is required!'
        assert data_length is not None, 'Argument "data_length" is required!'
        assert db_dir is not None, 'Argument "db_dir" is required!'
        assert table_name is not None, 'Argument "table_name" is required!'

        blank_space_criterion = MAX_CRITERION_CHARS - len(str(value))
        data = f'{value}{" " * blank_space_criterion}{" " * MAX_POSITION_CHARS * 2}'
        index_seq.write(codecs.encode(data.encode(), 'hex'))
        index_seq.flush()

        index_seq_size = os.stat(f'{db_dir}/index_{key}_{table_name}.bin').st_size
        result = VeskoReaderWriter.binary_search(index_seq, index_seq_size, value, data_length)
        VeskoReaderWriter.write_index_data_file(index_seq, index_data, position, result)

    @staticmethod
    def binary_search(index_seq, index_seq_size, c_value, data_length):
        start = 0
        end = index_seq_size
        middle = start + (end - start) // 2

        index_seq.seek(0 - data_length, io.SEEK_END)
        biggest_index = VeskoReaderWriter.read_index_file(index_seq)

        while True:
            remainder = middle % data_length

            if remainder != 0:
                middle -= remainder

            index_seq.seek(middle)

            data = VeskoReaderWriter.read_index_file(index_seq)

            if data[0] == c_value:
                return data

            elif c_value > data[0]:
                start = middle

            else:
                end = middle

            if end - start == data_length:
                print('No results found!')

                if c_value > biggest_index[0]:
                    return None, 1  # None = Not found, 1 = biggest

                else:
                    return None, -1  # -1 = less than biggest

            middle = start + (end - start) // 2

import codecs
import io
import os
from enum import Enum
from time import sleep


MAX_META_CHARS = 6
MAX_POINTER_CHARS = 20
MAX_CRITERIA_CHARS = 10
MAX_POSITION_CHARS = 12
DELETED_CHARS = 3


class DataType(Enum):
    INT = int
    TEXT = str


class LockFile:

    @staticmethod
    def lock(file: str):

        assert file is not None, 'Argument "file" is required!'

        try:
            open(f'{file}.lock', 'x')

        except FileExistsError:
            sleep(0.1)
            LockFile.lock(file)
            # print(f'Cannot lock "{file}". Already locked!')
            # raise

    @staticmethod
    def unlock(file: str):

        assert file is not None, 'Argument "file" is required!'

        try:
            os.remove(f'{file}.lock')

        except FileExistsError:
            sleep(0.1)
            LockFile.unlock(file)
            # print(f'Cannot unlock "{file}". File is not locked!')
            # raise


class VeskoReaderWriter:

    @staticmethod
    def encode_line(values: list, meta_length: int):

        values_len = []

        meta_data_size = len(values) * meta_length * 2 + DELETED_CHARS * 2
        blank_space = MAX_META_CHARS - len(str(meta_data_size))
        data = f'{meta_data_size}{" " * blank_space}'

        for value in values:
            value_len = len(value) * 2  # HEX len is twice the normal
            value_len_decimals = len(str(value_len))

            blank_space = meta_length - value_len_decimals

            values_len.append(f'{value_len}{" " * blank_space}')

        data += f'{"".join(values_len)} + {"".join(values)}'
        data = data.encode()
        return codecs.encode(data, 'hex')

    @staticmethod
    def raw_data_to_list(data_len: list, data: b''):
        result = []
        prev = 0

        for column_size in data_len:
            index = int(column_size / 2)
            value = data[prev:prev + index].decode()
            result.append(value)
            prev += index

        return result

    @staticmethod
    def read_file(f, meta_length: int, column_number: int = None, read_table: bool = False):
        while True:
            position = f.tell()

            if read_table and position == VeskoReaderWriter.read_pointer_info(f):
                break

            meta_size = f.read(MAX_META_CHARS * 2)
            meta_size = codecs.decode(meta_size, 'hex')

            if meta_size == b'':
                break

            meta = f.read(int(meta_size))
            meta_readable = codecs.decode(meta, 'hex')
            deleted = meta_readable[-3:]

            data_len = []
            for start in range(0, len(meta_readable) - 3, meta_length):
                data_len.append(int(meta_readable[start:start + meta_length]))

            if deleted == b' + ':
                if column_number is not None:
                    for index, column_len in enumerate(data_len):
                        if index == column_number:
                            data = f.read(column_len)
                            yield data, data_len, position, int(meta_size)

                        else:
                            f.seek(column_len, io.SEEK_CUR)

                else:
                    data = f.read(sum(data_len))
                    yield data, data_len, position, int(meta_size)

            else:
                f.seek(sum(data_len), io.SEEK_CUR)

    @staticmethod
    def read_table_file(f, meta_length: int, column_number: int = None):

        for row in VeskoReaderWriter.read_file(f, meta_length, column_number, True):
            data = codecs.decode(row[0], 'hex')

            if column_number is not None:
                yield data, row[2], row[3], row[1]

            else:
                yield VeskoReaderWriter.raw_data_to_list(row[1], data), row[2], row[3]

    @staticmethod
    def read_meta_file(f, meta_length: int):
        tables = dict()

        for row in VeskoReaderWriter.read_file(f, meta_length):
            data = codecs.decode(row[0], 'hex')
            prev = 0
            position = 0
            table_name = ''
            for count, column_size in enumerate(row[1]):
                if count % 2 != 0 or prev == 0:
                    index = int(column_size / 2)
                    name = data[prev:prev + index].decode()
                    prev += index

                    if prev - index == 0:
                        table_name = name
                        tables[table_name] = {}

                    else:
                        index1 = int(row[1][count + 1] / 2)
                        value = data[prev:prev + index1].decode()
                        tables[table_name][name] = getattr(DataType, value), position
                        prev += index1
                        position += 1

        return tables

    @staticmethod
    def read_pointer_info(f):
        pos = f.tell()
        f.seek(0)
        data = f.read(MAX_POINTER_CHARS * 2)
        data = codecs.decode(data, 'hex')
        f.seek(pos)

        return int(data)

    @staticmethod
    def write_pointer_info(f, position: int):
        blank_space = MAX_POINTER_CHARS - len(str(position))
        data = f'{position}{" " * blank_space}'
        data = data.encode()

        f.seek(0)
        f.write(codecs.encode(data, 'hex'))

    @staticmethod
    def read_index_file(f):
        # print('inti')
        deleted = f.read(DELETED_CHARS * 2)
        deleted = codecs.decode(deleted, 'hex')

        # print(deleted)
        if deleted == b' - ':
            # print('a')
            while True:
                # print('b')
                # print(f.read(44))
                f.seek(MAX_CRITERIA_CHARS * 2 + MAX_POSITION_CHARS * 2, io.SEEK_CUR)
                deleted_flag = f.read(DELETED_CHARS * 2)
                deleted_flag = codecs.decode(deleted_flag, 'hex')
                # print(deleted_flag)

                if deleted_flag != b' - ':
                    break

        criteria = f.read(MAX_CRITERIA_CHARS * 2)
        position = f.read(MAX_POSITION_CHARS * 2)

        # print(int(codecs.decode(criteria, 'hex')), int(codecs.decode(position, 'hex')))

        return int(codecs.decode(criteria, 'hex')), int(codecs.decode(position, 'hex'))

    @staticmethod
    def read_from_given_offset(f, offset: int, meta_length: int):
        f.seek(offset)
        meta_size = f.read(MAX_META_CHARS * 2)
        meta_size = codecs.decode(meta_size, 'hex')

        meta = f.read(int(meta_size))
        meta_readable = codecs.decode(meta, 'hex')
        deleted = meta_readable[-3:]

        data_len = []
        for start in range(0, len(meta_readable) - 3, meta_length):
            data_len.append(int(meta_readable[start:start + meta_length]))

        if deleted == b' + ':
            data = f.read(sum(data_len))
            return VeskoReaderWriter.raw_data_to_list(data_len, codecs.decode(data, 'hex'))

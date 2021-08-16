import codecs
import os
from enum import Enum
from time import sleep


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


def encode_line(values: list, meta_length: int):

    values_len = []

    for value in values:
        value_encoded = value.encode()
        value_hex = codecs.encode(value_encoded, 'hex')

        value_len = len(value_hex)
        value_len_decimals = len(str(value_len))

        blank_space = meta_length - value_len_decimals

        values_len.append(f'{value_len}{" " * blank_space}')

    data = f'{"".join(values_len)} + {" ".join(values)}'
    return codecs.encode(data.encode(), 'hex')

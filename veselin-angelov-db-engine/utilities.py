import os
from enum import Enum
from time import sleep


class DataType(Enum):
    INT = int
    TEXT = str


class WrongAmountOfValuesError(TypeError):
    pass


class TypesNotMatchError(TypeError):
    pass


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

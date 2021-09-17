import os
from time import sleep

from utilities import TableInTransactionException


class FileLocker:

    @staticmethod
    def __create_lock(file_name, mode):
        lock_name = f'{file_name}.{mode.value}.lock'
        pid = os.getpid()
        open(lock_name, 'x')
        file = open(lock_name, 'w')
        FileLocker.write_pid(file, pid)

    @staticmethod
    def lock(file_name: str):
        assert file_name is not None, 'Argument "file_name" is required!'

        try:
            lock_name = f'{file_name}.lock'
            pid = os.getpid()
            open(lock_name, 'x')
            file = open(lock_name, 'w')
            FileLocker.write_pid(file, pid)

        except FileExistsError:
            sleep(0.1)
            FileLocker.lock(file_name)
            # print(f'Cannot lock "{file}". Already locked!')
            # raise

    @staticmethod
    def unlock(file_name: str):
        assert file_name is not None, 'Argument "file_name" is required!'

        try:
            lock_name = f'{file_name}.lock'
            pid = os.getpid()
            file = open(lock_name, 'r')
            lock_pid = FileLocker.read_pid(file)

            if lock_pid == pid:
                os.remove(f'{file_name}.lock')

            else:
                raise TableInTransactionException

        except FileExistsError:
            sleep(0.1)
            FileLocker.unlock(file_name)
            # print(f'Cannot unlock "{file}". File is not locked!')
            # raise

    @staticmethod
    def write_pid(file, pid: int):
        file.write(str(pid))

    @staticmethod
    def read_pid(file):
        pid = file.read()
        return int(pid)

    @staticmethod
    def check_lock(file_name: str):
        assert file_name is not None, 'Argument "file_name" is required!'

        lock_name = f'{file_name}.lock'
        return os.path.isfile(lock_name)

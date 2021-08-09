from enum import Enum


class Status(Enum):
    OK = 200, 'OK'
    NOT_FOUND = 404, 'Not Found'
    INTERNAL_SERVER_ERROR = 500, 'Internal Server Error'


def read_in_chunks(file_object, chunk_size=1024):
    while True:
        data = file_object.read(chunk_size)
        if not data:
            break
        yield data

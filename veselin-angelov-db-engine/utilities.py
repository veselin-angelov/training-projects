from enum import Enum


class DataType(Enum):
    INT = int
    TEXT = str


class WrongAmountOfValuesError(TypeError):
    pass


class TypesNotMatchError(TypeError):
    pass

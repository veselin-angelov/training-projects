import codecs

META = 15

# try:
# codecs.open('test.bin', 'wb')

# except FileExistsError:
#     pass

# f = codecs.open('test.bin', 'rb+')
# f = codecs.open('test.bin', 'ab+')

# a = 'test string\n asdsad'

data = ['asd', 'test', 'password']


# a = ' '.join(data)

# print(len(a))
# print(a)


# # b = ''.join(map(bin, bytearray(a, 'utf-8')))

# # print(len(b))
# # print(b)

# # f.write(b.encode())
# # f.write(a.encode())
# # f.write(hex(a).encode())

# # new_a = ''

# # for i in a:
# #     ii = int(i, 16)
# #     ix = hex(ii)
# #     new_a += ix


# # ai = int(a, 16)
# # ax = hex(ai)

# # f.write(a.hex().encode())

# a = a.encode()

# ae = codecs.encode(a, "hex")


# len_ae = len(ae)
# # len_ae = 7878978

# len_d_ae = len(str(len_ae))

# # print(len_ae)
# # print(len_d_ae)

# space = META - len_d_ae - 3

# print(space)

# all = f'{len_ae}{" " * space} + {a.decode()}'

# # all += ' ' * space

# # for i in range(space):
# #     all += ' '

# # all += f'+ {a.decode()}'

# alle = codecs.encode(all.encode(), "hex")

# f.write(alle)

# f.flush()
# f.seek(0)

# line = f.readline()

# print(line.decode().decode("hex"))
# print(line)
# print(codecs.decode(line, "hex"))


def encode_line(values: list, meta_length: int):
    values_len = []

    for value in values:
        value_encoded = value.encode()
        value_hex = codecs.encode(value_encoded, 'hex')

        value_len = len(value_hex)
        value_len_decimals = len(str(value_len))

        blank_space = meta_length - value_len_decimals

        values_len.append(f'{value_len}{" " * blank_space}')

    data = f'{"".join(values_len)} + {"".join(values)}'
    return codecs.encode(data.encode(), 'hex')


def delete_row(row_number: int):
    f = codecs.open('test.bin', 'wb')
    f.seek(0)
    f.seek(92)

    f.write(codecs.encode('-'.encode(), 'hex'))


def write_line():
    data = ['asd', 'test', 'password']
    f = codecs.open('test.bin', 'ab')
    h = encode_line(data, META)
    f.write(h)


def read_line():
    f = codecs.open('test.bin', 'rb')
    line = f.readline()

    print(line)
    print(codecs.decode(line, "hex"))


def read_file(columns: int):
    f = codecs.open('test.bin', 'rb')

    row = 0

    while True:
        meta = f.read((META * 2 * columns) + 6)

        if meta == b'':
            break

        row += 1

        meta_readable = codecs.decode(meta, 'hex')

        deleted = meta_readable[-3:]

        if deleted == b' + ':
            data_len = []
            for start in range(0, len(meta_readable) - 3, META):
                data_len.append(int(meta_readable[start:start + META]))

            data = f.read(sum(data_len))

            yield data, data_len, row


if __name__ == '__main__':
    a = read_file(3)

    tables = dict()

    for i in a:
        data = codecs.decode(i[0], 'hex')
        prev = 0
        table_name = ''
        for o in i[1]:
            index = int(o / 2)
            name = data[prev:prev + index].decode()
            if prev == 0:
                table_name = name
                tables[table_name] = []

            else:
                tables[table_name].append(name)
            prev += index

    print(tables)

# f.seek(0)
# f.seek(92)

# f.write(codecs.encode('-'.encode(), 'hex'))

# f.seek(0)

# line = f.readline()

# print(line)

# print(codecs.decode(line, "hex"))

#!/usr/bin/python3

import asyncio
import datetime
import json
import os
import socket
import time
from subprocess import Popen, PIPE

# import aiofiles
# from concurrent.futures import ThreadPoolExecutor

from utilities import Status, read_in_chunks

# executor = ThreadPoolExecutor()

CHUNK_SIZE = 10000

mime_types = {
    '.html': 'text/html',
    '.js': 'text/javascript',
    '.css': 'text/css',
    '.json': 'application/json',
    '.png': 'image/png',
    '.jpg': 'image/jpg',
    '.gif': 'image/gif',
    '.svg': 'image/svg+xml',
    '.wav': 'audio/wav',
    '.mp4': 'video/mp4',
    '.woff': 'application/font-woff',
    '.ttf': 'application/font-ttf',
    '.eot': 'application/vnd.ms-fontobject',
    '.otf': 'application/font-otf',
    '.wasm': 'application/wasm'
}


# def stream_file(filename, sock, writer):
#     # sock.setblocking(1)
#
#     with open(f'.{filename}', 'rb') as f:
#         for chunk in read_in_chunks(f, chunk_size=4096):
#             sock.sendall(chunk)
#
#     sock.close()
#     writer.close()


def make_response_headers(status, path=None):
    response_line = f"HTTP/1.1 {status.value[0]} {status.value[1]}\r\n"

    headers = "".join([
        "Server: Test Server\r\n",
        f"Date: {datetime.datetime.now(datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT')}\r\n"
    ])

    if path:
        filename, file_extension = os.path.splitext(path)
        headers += f"Content-Type: {mime_types[file_extension] if file_extension in mime_types.keys() else 'application/octet-stream'}\r\n"

    blank_line = "\r\n"
    response_headers = "".join([response_line, headers, blank_line])

    return response_headers


async def handle_response(request, writer):
    try:
        if os.path.isfile(f"./cgi-bin{request['url']}"):
            pass

        elif os.path.isfile(f".{request['url']}"):
            pass

        else:
            raise IOError

    except IOError as e:
        response_headers = make_response_headers(status=Status.NOT_FOUND)
        writer.write(response_headers.encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        print(e)
        return

    try:
        if os.path.isfile(f"./cgi-bin{request['url']}"):
            response_headers = make_response_headers(status=Status.OK, path='a.html')
            writer.write(response_headers.encode())
            await writer.drain()

            process = Popen(['./cgi-bin/mod_python.py'], stdout=PIPE, stdin=PIPE, stderr=PIPE)

            response_headers_dict = {
                'CONTENT_TYPE': mime_types['.html'],
                'DATE_GMT': datetime.datetime.now(datetime.timezone.utc).strftime('%a, %d %b %Y %H:%M:%S GMT'),
                'DATE_LOCAL': datetime.datetime.now().strftime('%a, %d %b %Y %H:%M:%S'),
                'SERVER_SOFTWARE': 'Na Vesko server-a/alpha v1.0',
                'REMOTE_ADDR': writer.get_extra_info(name='socket').getpeername()[0],
                'SERVER_ROOT': os.getcwd(),
                'PATH_TRANSLATED': os.path.dirname(os.path.abspath(__file__)),
                'DOCUMENT_ROOT': os.path.dirname(os.path.abspath(__file__)) + '/cgi-bin/'
            }

            request['response_headers'] = response_headers_dict

            process.communicate(input=json.dumps(request).encode())

            if process.communicate()[1]:
                print('stderr: ', process.communicate()[1])

            writer.write(process.communicate()[0])
            await writer.drain()

            writer.close()
            await writer.wait_closed()

        elif os.path.isfile(f".{request['url']}"):
            response_headers = make_response_headers(status=Status.OK, path=request['url'])
            writer.write(response_headers.encode())
            await writer.drain()

            # loop = asyncio.get_running_loop()

            # fin = open(f'.{request["url"]}', 'rb')
            # await loop.sendfile(fin)

            # sock = writer.get_extra_info(name='socket')
            # with ThreadPoolExecutor() as pool:
            #     result = await loop.run_in_executor(
            #         pool, stream_file, request.get('url'), sock, writer)
            #
            #     print('default thread pool', result)

            with open(f'.{request["url"]}', 'rb') as fin:
                contents = fin.read(CHUNK_SIZE)
                while contents:
                    writer.write(contents)
                    contents = fin.read(CHUNK_SIZE)
                await writer.drain()

            writer.close()
            await writer.wait_closed()

            # fin = open(f'.{request["url"]}', 'rb')
            # os.set_blocking(fin.fileno(), False)
            # print(request['id'])
            # for chunk in read_in_chunks(fin, chunk_size=4096):
            #     writer.write(chunk)
            #     await writer.drain()
            #
            # fin.close()
            # s = time.time()
            # async with aiofiles.open(f'.{request["url"]}', mode='rb') as f:
            #     # print(request['id'])
            #     contents = await f.read(4096)
            #     while contents:
            #         writer.write(contents)
            #         await writer.drain()
            #         contents = await f.read(4096)
            # e = time.time()
            # print(e - s)

            # future_file = executor.submit(read_file, f'.{request["url"]}')
            # future_file.add_done_callback(on_file_streaming_finished)

            # if future_file.done():
            #     print(future_file.result())
            # await writer.drain()
            #
            # writer.close()
            # await writer.wait_closed()

        else:
            raise IOError

    except Exception as e:
        response_headers = make_response_headers(status=Status.INTERNAL_SERVER_ERROR)
        writer.write(response_headers.encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        print(e)
        return


async def handle_request(reader, writer):
    try:
        data = await reader.readuntil(b'\r\n\r\n')

        headers_end = data.index(b'\r\n\r\n')
        request_headers = data[:headers_end]
        request_headers_list = request_headers.split(b'\r\n')
        request_headers_lines = []

        for request_line in request_headers_list:
            request_headers_lines.append(request_line.decode().split(' '))

        request_url = request_headers_lines[0][1].split('?')

        headers = {}

        for index, header in enumerate(request_headers_lines):
            if index == 0:
                continue

            headers[header[0][:-1]] = header[1]

        request = {
            "method": request_headers_lines[0][0],
            "url": request_url[0],
            "args": request_url[1] if len(request_url) > 1 else None,
            "http_version": request_headers_lines[0][2].split('/')[1],
            "headers": headers,
        }

        print(f"{datetime.datetime.now().isoformat()} - HTTP {request['http_version']} "
              f"{request['method']} {request['url']}")

        await handle_response(request, writer)

    except Exception as e:
        response_headers = make_response_headers(status=Status.INTERNAL_SERVER_ERROR)
        writer.write(response_headers.encode())
        await writer.drain()
        writer.close()
        await writer.wait_closed()
        print(e)
        return


async def main():
    try:
        server = await asyncio.start_server(handle_request, family=socket.AF_INET, host='', port=8889)

        print(f'Serving on {server.sockets[0].getsockname()}')

        async with server:
            await server.serve_forever()

    except Exception as e:
        print(e)


if __name__ == '__main__':
    asyncio.run(main())

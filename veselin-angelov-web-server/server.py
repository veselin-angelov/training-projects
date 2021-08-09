#!/usr/bin/python3
import datetime
import errno
import json
import os
import socket
from subprocess import Popen, PIPE
from utilities import Status, read_in_chunks

SERVER_ADDRESS = (HOST, PORT) = '', 8889
REQUEST_QUEUE_SIZE = 1


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


def make_response_headers(status, path=None):
    response_line = f"HTTP/1.1 {status.value[0]} {status.value[1]}\r\n"

    headers = "Server: Test Server\r\n"

    if path:
        filename, file_extension = os.path.splitext(path)
        headers += f"Content-Type: {mime_types[file_extension] if file_extension in mime_types.keys() else 'application/octet-stream'}\r\n"

    blank_line = "\r\n"
    response_headers = "".join([response_line, headers, blank_line])

    return response_headers


def handle_response(request, client_connection):
    try:
        if os.path.isfile(f"./cgi-bin{request['url']}"):
            pass

        else:
            fin = open(f'.{request["url"]}')

    except IOError as e:
        response_headers = make_response_headers(status=Status.NOT_FOUND)
        client_connection.sendall(response_headers.encode())
        client_connection.close()
        print(e)
        return

    try:
        if os.path.isfile(f"./cgi-bin{request['url']}"):
            response_headers = make_response_headers(status=Status.OK, path='a.html')
            client_connection.sendall(response_headers.encode())

            process = Popen(['./cgi-bin/mod_python.py'], stdout=PIPE, stdin=PIPE, stderr=PIPE)

            # TUKA
            process.communicate(input=json.dumps(request).encode())

            if process.communicate()[1]:
                print('stderr: ', process.communicate()[1])

            client_connection.sendall(process.communicate()[0])
            client_connection.close()

        else:
            response_headers = make_response_headers(status=Status.OK, path=request['url'])
            client_connection.sendall(response_headers.encode())

            for chunk in read_in_chunks(fin):
                client_connection.sendall(chunk.encode())

            fin.close()
            client_connection.close()

    except Exception as e:
        response_headers = make_response_headers(status=Status.INTERNAL_SERVER_ERROR)
        client_connection.sendall(response_headers.encode())
        client_connection.close()
        print(e)
        return


def handle_request(client_connection):
    data = client_connection.recv(1024)

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

        headers[header[0]] = header[1]

    request = {
        "method": request_headers_lines[0][0],
        "url": request_url[0],
        "args": request_url[1] if len(request_url) > 1 else None,
        "http_version": request_headers_lines[0][2].split('/')[1],
        "headers": headers,
    }

    print(f"{datetime.datetime.now().isoformat()} - HTTP {request['http_version']} {request['method']} {request['url']}")

    handle_response(request, client_connection)


def serve_forever():
    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(SERVER_ADDRESS)
    listen_socket.listen(REQUEST_QUEUE_SIZE)
    print('Serving HTTP on port {port} ...'.format(port=PORT))

    while True:
        try:
            client_connection, client_address = listen_socket.accept()

        except IOError as e:
            code, msg = e.args
            # restart 'accept' if it was interrupted
            if code == errno.EINTR:
                continue
            else:
                raise

        try:
            handle_request(client_connection)

        except Exception as e:
            print(e)

    listen_socket.close()


if __name__ == '__main__':
    serve_forever()

import errno
import os
import signal
import socket
import time

SERVER_ADDRESS = (HOST, PORT) = '', 8889
REQUEST_QUEUE_SIZE = 1


def handle_request(client_connection):
    data = client_connection.recv(1024)
    print(data)

    marker = data.index(b'\r\n\r\n')

    print(marker)

    request_headers = data[:marker]

    print(request_headers)

    request_headers_list = request_headers.split(b'\r\n')

    print(request_headers_list)

    request_lines = []

    for header in request_headers_list:
        request_lines.append(header.split(b' '))

    print(request_lines)

    try:
        fin = open('./files/1kb.json')
        content = fin.read()
        fin.close()

        response_line = "HTTP/1.1 200 OK\r\n"

        headers = "".join([
            "Server: Test Server\r\n",
            "Content-Type: application/json\r\n"
        ])

        blank_line = "\r\n"
        resp = "".join([response_line, headers, blank_line, content])
        client_connection.sendall(resp.encode())
        client_connection.close()

    except Exception as e:
        print(e)
    # time.sleep(60) concurrency test


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

        handle_request(client_connection)

    listen_socket.close()


if __name__ == '__main__':
    serve_forever()

#!/usr/bin/python3
import json
import sys
import time
from os import environ


try:
    data = json.loads(input())

    response_headers = data.get('response_headers')

    environ['GATEWAY_INTERFACE'] = 'CGI/1.1'
    environ['SERVER_PROTOCOL'] = 'HTTP/1.1'
    environ['REQUEST_METHOD'] = data.get('method')
    environ['QUERY_STRING'] = data.get('args') if data.get('args') else ''
    environ['PATH_INFO'] = data.get('url')
    environ['SCRIPT_NAME'] = f'./cgi-bin/{data.get("url")}'
    environ['SERVER_NAME'] = 'localhost'
    environ['SERVER_PORT'] = '8889'
    environ['DATE_GMT'] = response_headers.get('DATE_GMT')
    environ['DATE_LOCAL'] = response_headers.get('DATE_LOCAL')
    environ['CONTENT_TYPE'] = response_headers.get('CONTENT_TYPE')
    environ['SERVER_SOFTWARE'] = response_headers.get('SERVER_SOFTWARE')
    environ['REMOTE_ADDR'] = response_headers.get('REMOTE_ADDR')
    environ['SERVER_ROOT'] = response_headers.get('SERVER_ROOT')
    environ['PATH_TRANSLATED'] = response_headers.get('PATH_TRANSLATED')
    environ['DOCUMENT_ROOT'] = response_headers.get('DOCUMENT_ROOT')

    exec(open(f'./cgi-bin{environ["PATH_INFO"]}').read())

except Exception as e:
    print(e, file=sys.stderr)

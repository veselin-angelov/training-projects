#!/usr/bin/python3
import json
import sys
import time
from os import environ


try:
    data = json.loads(input())

    environ['GATEWAY_INTERFACE'] = 'CGI/1.1'
    environ['SERVER_PROTOCOL'] = 'HTTP/1.1'
    environ['REQUEST_METHOD'] = data.get('method')
    environ['QUERY_STRING'] = data.get('args') if data.get('args') else ''
    environ['PATH_INFO'] = data.get('url')
    environ['SCRIPT_NAME'] = f'./cgi-bin/{data.get("url")}'
    environ['SERVER_NAME'] = 'localhost'
    environ['SERVER_PORT'] = '8889'

    exec(open(f'./cgi-bin{environ["PATH_INFO"]}').read())

except Exception as e:
    print(e, file=sys.stderr)

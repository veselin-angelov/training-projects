#!/usr/bin/python3
import cgi
import cgitb
import sys


cgitb.enable()
cgi.test()

try:
    data = cgi.FieldStorage()
    a = data['a'].value
    b = data['b'].value
    print(int(a) + int(b))

except Exception as e:
    print(e, file=sys.stderr)

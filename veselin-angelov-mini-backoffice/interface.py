import sys
import json

from main import DbEngine


engine = DbEngine()
db_name = 'backoffice'
engine.use_db(db_name)
db_table = 'users'

command = sys.argv[1]
credentials = json.loads(sys.argv[2])

if not credentials.get('username'):
    print('Credentials not supplied properly!', file=sys.stderr)
    exit(-1)

elif (not credentials.get('username') or not credentials.get('password')) and command == 'insert':
    print('Credentials not supplied properly!', file=sys.stderr)
    exit(-1)


if command == 'select':
    rows = engine.select(db_table, {'username': credentials.get('username')})
    for row in rows:
        row_dict = {
            'id': int(row[0]),
            'username': row[1],
            'password': row[2]
        }
        print(json.dumps(row_dict))

elif command == 'insert':
    file = open(f'{engine.db_directory}/last_id.bin', 'r+')
    last_id = int(file.readline(1))

    engine.insert(db_table, {'id': last_id + 1, 'username': credentials.get('username'), 'password': credentials.get('password')})

    file.seek(0)
    file.write(str(last_id + 1))

else:
    print('Invalid command!', file=sys.stderr)
    exit(-1)

sys.stdout.flush()
sys.stderr.flush()

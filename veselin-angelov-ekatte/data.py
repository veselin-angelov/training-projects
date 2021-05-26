from helpers import create_connection, fetchall, fetchone

connection = create_connection(
    "ekatte", "postgres", "admin", "127.0.0.1", "5432"
)


def get_data(search):
    q = f"SELECT s.ekatte, s.type, s.name, m.name, a.name FROM settlements s LEFT JOIN municipalities m ON s.municipality_code=m.code LEFT JOIN areas a ON m.area_code=a.code WHERE LOWER(s.name) LIKE '%{search.lower()}%';"
    responses = fetchall(connection, q)

    return responses


def get_stats():
    stats = dict()

    q = f'SELECT COUNT(*) FROM areas;'
    r = fetchone(connection, q)
    stats['areas'] = r[0]

    q = f'SELECT COUNT(*) FROM municipalities;'
    r = fetchone(connection, q)
    stats['municipalities'] = r[0]

    q = f'SELECT COUNT(*) FROM settlements;'
    r = fetchone(connection, q)
    stats['settlements'] = r[0]

    return stats

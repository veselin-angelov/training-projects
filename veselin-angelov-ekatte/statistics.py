from helpers import fetchone


def get_stats(connection):
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

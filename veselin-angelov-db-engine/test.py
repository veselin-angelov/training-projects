from main import DbEngine


def test_insert():
    engine = DbEngine()

    engine.use_db('test')

    user5 = {
        'user_id': 7,
        'username': 'obo',
        'password': 'obo'
    }

    engine.insert('users', user5)


if __name__ == '__main__':
    test_insert()

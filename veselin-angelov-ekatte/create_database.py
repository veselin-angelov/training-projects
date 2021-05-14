from helpers import create_connection, execute_query

connection = create_connection(
    "postgres", "postgres", "admin", "127.0.0.1", "5432"
)

create_database_query = "CREATE DATABASE ekatte"
execute_query(connection, create_database_query)

connection = create_connection(
    "ekatte", "postgres", "admin", "127.0.0.1", "5432"
)

create_area_query = '''
    CREATE TABLE IF NOT EXISTS "areas" (
        "id" serial NOT NULL UNIQUE,
        "name" TEXT NOT NULL UNIQUE,
        "code" TEXT NOT NULL UNIQUE,
        CONSTRAINT "area_pk" PRIMARY KEY ("code")
    );
'''

create_municipality_query = '''
    CREATE TABLE IF NOT EXISTS "municipalities" (
        "id" serial NOT NULL UNIQUE,
        "name" TEXT NOT NULL,
        "code" TEXT NOT NULL UNIQUE,
        "area_code" TEXT NOT NULL,
        CONSTRAINT "municipalities_pk" PRIMARY KEY ("code"),
        CONSTRAINT "municipalities_fk0" FOREIGN KEY ("area_code") REFERENCES "areas"("code")
    );
'''

create_settlements_query = '''
    CREATE TABLE IF NOT EXISTS "settlements" (
        "id" serial NOT NULL,
        "ekatte" TEXT NOT NULL UNIQUE,
        "type" TEXT NOT NULL,
        "name" TEXT NOT NULL,
        "municipality_code" TEXT NOT NULL,
        CONSTRAINT "settlements_pk" PRIMARY KEY ("id"),
        CONSTRAINT "settlements_fk0" FOREIGN KEY ("municipality_code") REFERENCES "municipalities"("code")
    );
'''

execute_query(connection, create_area_query)
execute_query(connection, create_municipality_query)
execute_query(connection, create_settlements_query)

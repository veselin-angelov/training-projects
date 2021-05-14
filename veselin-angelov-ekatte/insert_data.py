from helpers import create_connection, execute_query
import pandas as pd

connection = create_connection(
    "ekatte", "postgres", "admin", "127.0.0.1", "5432"
)

areas = pd.read_excel(r'/home/vesko/Documents/tb-prac/ekatte-xlsx/Ek_obl.xlsx')
municipalities = pd.read_excel(r'/home/vesko/Documents/tb-prac/ekatte-xlsx/Ek_obst.xlsx')
settlements = pd.read_excel(r'/home/vesko/Documents/tb-prac/ekatte-xlsx/Ek_atte.xlsx')

for i in range(len(areas)):
    q = f'INSERT INTO areas (name, code) VALUES (%s, %s);'
    values = (areas["name"][i], areas["oblast"][i])
    execute_query(connection, q, values)

for i in range(len(municipalities)):
    q = f'INSERT INTO municipalities (name, code, area_code) VALUES (%s, %s, %s);'
    values = (municipalities["name"][i], municipalities["obstina"][i], municipalities["obstina"][i][:3])
    execute_query(connection, q, values)

for i in range(1, len(settlements)):
    q = f'INSERT INTO settlements (ekatte, type, name, municipality_code) VALUES (%s, %s, %s, %s);'
    values = (str(settlements["ekatte"][i]), settlements["t_v_m"][i], settlements["name"][i], settlements["obstina"][i])
    execute_query(connection, q, values)

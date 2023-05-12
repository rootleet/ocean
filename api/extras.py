import pyodbc

from ocean.settings import DB_SERVER, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD



def cmm_connect():
    server = f"{DB_SERVER},{DB_PORT}"
    database = DB_NAME
    username = DB_USER
    password = DB_PASSWORD
    driver = '{ODBC Driver 17 for SQL Server}'  # Change this to the driver you're using
    connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    return pyodbc.connect(connection_string)
    # return connection.cursor()
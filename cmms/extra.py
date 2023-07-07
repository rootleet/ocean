import pyodbc
from ocean.settings import DB_SERVER, DB_NAME, DB_USER, DB_PORT, DB_PASSWORD


def db():
    server = f"{DB_SERVER},{DB_PORT}"
    database = DB_NAME
    username = DB_USER
    password = DB_PASSWORD
    driver = '{ODBC Driver 17 for SQL Server}'  # Change this to the driver you're using
    connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    connection = pyodbc.connect(connection_string)
    return connection.cursor()
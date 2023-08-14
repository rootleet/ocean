import pyodbc
from ocean.settings import DB_SERVER, DB_NAME, DB_USER, DB_PORT, DB_PASSWORD


# connect to db
def db(host=DB_SERVER, port=DB_PORT, db=DB_NAME, user=DB_USER, password=DB_PASSWORD):
    server = f"{host},{port}"
    database = db
    username = user
    password = password
    driver = '{ODBC Driver 17 for SQL Server}'  # Change this to the driver you're using
    connection_string = f"DRIVER={driver};SERVER={server};DATABASE={database};UID={username};PWD={password}"
    connection = pyodbc.connect(connection_string)
    return connection.cursor()


# DB_CURSOR = db()

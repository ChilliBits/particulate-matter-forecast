import mysql.connector
import os

server_host = os.environ["PMAPI_FORECAST_HOST"]
server_user = os.environ["PMAPI_FORECAST_USER"]
server_password = os.environ["PMAPI_FORECAST_PASSWORD"]

def connectToDb(db_name):
    return mysql.connector.connect(host=server_host, user=server_user, passwd=server_password, database=db_name)

def connectToDbServer():
    return mysql.connector.connect(host=server_host, user=server_user, passwd=server_password)
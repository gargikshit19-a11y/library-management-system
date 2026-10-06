import os
import mysql.connector
from mysql.connector import Error

def get_db_config():
    return {
        'host': os.environ.get('DB_HOST', 'localhost'),
        'user': os.environ.get('DB_USER', 'root'),
        'password': os.environ.get('DB_PASSWORD', ''),
        'database': os.environ.get('DB_NAME', 'library_management'),
        'port': int(os.environ.get('DB_PORT', 3306)),
    }

def get_connection():
    try:
        config = get_db_config()
        connection = mysql.connector.connect(**config)
        return connection
    except Error as e:
        raise e

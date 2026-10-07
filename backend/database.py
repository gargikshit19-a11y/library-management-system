import os
import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def get_db_config():
    return {
        'host': os.getenv('DB_HOST', 'localhost'),
        'user': os.getenv('DB_USER', 'libuser'),
        'password': os.getenv('DB_PASSWORD', 'LibPass#2026!'),
        'database': os.getenv('DB_NAME', 'library_management'),
        'port': int(os.getenv('DB_PORT', 3306)),
    }

def get_connection():
    try:
        config = get_db_config()
        connection = mysql.connector.connect(**config)
        return connection
    except Error as e:
        raise e

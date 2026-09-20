import mysql.connector
import os

if os.getenv("DB_HOST"):
    # Aiven / deployed database
    db = mysql.connector.connect(
        host=os.getenv("DB_HOST"),
        port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD"),
        database=os.getenv("DB_NAME"),
        ssl_ca=os.getenv("DB_SSL_CA")
    )
else:
    # Local XAMPP MySQL
    db = mysql.connector.connect(
        host="localhost",
        user="root",
        password="",
        database="student_network"
    )


def get_cursor():
    return db.cursor(dictionary=True)
import mysql.connector
from mysql.connector import Error

def connect_mysql():
    try:
        connection = mysql.connector.connect(
            host='localhost',
            user='admin',
            password='distribuidos123',
            database='hospital',
        )

        if connection.is_connected():
            print("Conexión exitosa con la base de datos")

            cursor = connection.cursor()
            cursor.execute("SELECT DATABASE();")
            registro = cursor.fetchone()
            print("Conectado a la base de datos: ", registro)
    
    except Error as e:
        print("Error al concentar a MySQL: ", e)
    
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()
            print("Conexión a MySQL cerrada")

if __name__ == "__main__":
    connect_mysql()
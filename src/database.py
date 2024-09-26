import mysql.connector

database = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="0000",
    database="sistemaciclassena"
)

print(database, "Conectado")
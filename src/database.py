import mysql.connector

database = mysql.connector.connect(
    host="localhost",
    user="root",
    passwd="root",
    database="sistemaciclassena"
)

print(database, "Conectado")
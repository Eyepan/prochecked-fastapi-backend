import mysql.connector

config = {
    "user": "root",
    "password": "",
    "host": "localhost",
    "database": "prochecked",
    "port": 3306,
    "raise_on_warnings": False,
}


mysql = mysql.connector.connect(**config)

cursor = mysql.cursor()

# nope, not touching this
cursor.execute("SET FOREIGN_KEY_CHECKS=0")

cursor.execute("SHOW TABLES")
tables = cursor.fetchall()
for table in tables:
    cursor.execute("DROP TABLE %s" % table[0])


cursor.execute("SET FOREIGN_KEY_CHECKS=1")

cursor.close()
mysql.close()

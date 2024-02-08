import sqlite3

connection = sqlite3.connect('bot.sqlite')
cursor = connection.cursor()
cursor.execute("INSERT INTO coins (nameds, coin) VALUES ('battlepetrovich', 200) ")
connection.commit()
connection.close()
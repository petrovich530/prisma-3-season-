import sqlite3

connection = sqlite3.connect('bot.sqlite')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS coins (
nameds TEXT NOT NULL,
coin INTEGER,
PRIMARY KEY (nameds)
)
''')

cursor.execute("INSERT INTO coins (nameds, coin) VALUES ('bubble', 200) ")


connection.commit()
connection.close()
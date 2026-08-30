import sqlite3

conn = sqlite3.connect("db/mydb.db")
conn.row_factory = sqlite3.Row
for row in conn.execute('SELECT * FROM users'):
    print(dict(row))
for row in conn.execute("SELECT * FROM videos"):
    print(dict(row))
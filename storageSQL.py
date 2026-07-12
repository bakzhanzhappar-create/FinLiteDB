import sqlite3

db = sqlite3.connect('bagatest.db')

cursor= db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS bagatabletest
""")

db.close()
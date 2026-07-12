import sqlite3

db = sqlite3.connect('bagatest.db')

cursor= db.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS bagatabletest(
    id PRIMARY KEY NOT NULL,
    name TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS payments_table(
    payment_type TEXT NOT NULL,
    value FLOAT NOT NULL,
    description TEXT
    )

""")

db.close()
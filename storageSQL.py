import sqlite3

db = sqlite3.connect('bagatest.db')
cursor= db.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

cursor.execute("""
CREATE TABLE IF NOT EXISTS template_table(
    id INT PRIMARY KEY NOT NULL,
    name TEXT NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS payments_table(
    template_id INT NOT NULL,
    payment_type TEXT NOT NULL,
    value REAL NOT NULL,
    description TEXT,
    FOREIGN KEY (template_id) REFERENCES template_table(id)
    )

""")
try:
    db.execute("BEGIN TRANSACTION")
    cursor.execute(""" INSERT INTO template_table(name) VALUES ('example_name')""")

db.close()
#оказывается на sqlite3, вместо float используется real
#не надо юзать autoincrement, sqlite3 сам добавляет номер id по существующих аттрибутов таблиц
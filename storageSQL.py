import sqlite3

db = sqlite3.connect('bagatest.db')
cursor= db.cursor()
cursor.execute("PRAGMA foreign_keys = ON;")

cursor.execute("""
CREATE TABLE IF NOT EXISTS template_table(
    id INTEGER PRIMARY KEY,
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
    with db:
        cursor.execute(""" INSERT INTO template_table(name) VALUES ('example_name')""")

        generated_id=cursor.lastrowid

        cursor.execute(""" INSERT INTO payments_table(template_id, payment_type, value, description) VALUES (?, 'f', 12134, 'nigga nigga nigga')""", (generated_id,))

        print("Template table created successfully")

except sqlite3.Error as error:
    print(f"Something went wrong: {error}")

finally:
    cursor.close()
    db.close()

#оказывается на sqlite3, вместо float используется real
#не надо юзать autoincrement, sqlite3 сам добавляет номер id по существующих аттрибутов таблиц
 #Откат (rollback) произойдет автоматически благодаря контекстному менеджеру 'with db'
import sqlite3

db = sqlite3.connect('bagatest.db')

cursor= db.cursor()

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
    value FLOAT NOT NULL,
    description TEXT,
    FOREIGN KEY (template_id) REFERENCES template_table(id)
    )

""")

db.close()
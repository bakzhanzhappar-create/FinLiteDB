import sqlite3
# print("Coming soon!")
db=sqlite3.connect('test.db')
cursor=db.cursor()

# Создание таблицы
# cursor.execute("""CREATE TABLE tabletest(
#     Type text,
#     Source text,
#     Income int
# )"""
# )

# Заполнение данными
# cursor.execute("INSERT INTO tabletest VALUES('Extra', 'from parents', 3000)")

cursor.execute("SELECT rowid, * FROM tabletest WHERE Income > 20000")
# print(cursor.fetchall())

items=cursor.fetchall()
for el in items:
    print(el[1]+"\n")
    print(f"{el[3]}")

# print(cursor.fetchmany(2))
# print(cursor.fetchone()[1])

# rowid он встроенный, не надо парится
db.commit()
db.close
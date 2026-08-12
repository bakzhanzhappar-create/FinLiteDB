import sqlite3
from decimal import Decimal
from domain import Template, Validator, Fix, Percentage
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

DB_PATH = (BASE_DIR / "data" / "finlite.db").resolve()


class NotFoundError(Exception):
    ...


def get_db_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"Connecting to {DB_PATH.as_posix()}", flush=True)

    db = sqlite3.connect(DB_PATH)
    db.execute("PRAGMA foreign_keys = ON;")
    return db

def init_db():
    db = get_db_connection()
    cursor = db.cursor()
    try:
        with db:
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
        print("База данных SQL и таблицы успешно проверены/созданы.")
    except sqlite3.Error as error:
        print(f"Ошибка при автоматическом создании базы данных: {error}")
    finally:
        cursor.close()
        db.close()


def packing_to_sql(template_object: Template):
    print(f"Unpacking template: {template_object.name}")
    print("SAVING TO SQLITE... ")

    db = get_db_connection()
    cursor = db.cursor()

    try:
        with db:
            cursor.execute("DELETE FROM payments_table WHERE template_id = (SELECT id FROM template_table WHERE name = ?)",(template_object.name,))
            cursor.execute("DELETE FROM template_table WHERE name = ?", (template_object.name,))

            cursor.execute("INSERT INTO template_table (name) VALUES (?)",(template_object.name,))
            generated_id = cursor.lastrowid

            for payment in template_object.payments:
                payment_type = type(payment).__name__

                value_to_save = float(payment.value)
                description = payment.description

                cursor.execute(
                    """
                    INSERT INTO payments_table (template_id, payment_type, value, description)
                    VALUES (?, ?, ?, ?)
                    """,
                    (generated_id, payment_type, value_to_save, description)
                )
        print("done")
        return True

    except sqlite3.Error as error:
        print(f"Database error during save: {error}")
        raise error
    finally:
        cursor.close()
        db.close()


def template_from_sql(target_name: str) -> Template:
    print(f"Reading files from SQL for: {target_name}... ")

    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT id, name FROM template_table WHERE name = ?", (target_name,))
        template_row = cursor.fetchone()

        if template_row is None:
            raise NotFoundError(f"Ur asked {target_name} doesnt exist in Database")

        template_id, template_name = template_row

        cursor.execute(
            """
            SELECT payment_type, value, description FROM payments_table WHERE template_id = ?
            """,(template_id,))
        payments_rows = cursor.fetchall()

        cleaned_payments = list()

        for percent_type, raw_value, description in payments_rows:
            checked_value = Validator(value=str(raw_value), target_type=Decimal)
            decimal_value = checked_value.value

            if percent_type == 'Percentage':
                obj = Percentage(value=decimal_value, description=description)
            else:
                obj = Fix(value=decimal_value, description=description)

            cleaned_payments.append(obj)

        return Template(name=template_name, payments=cleaned_payments)

    except sqlite3.Error as error:
        print(f"Database error during read: {error}")
        raise error
    finally:
        cursor.close()
        db.close()


def sql_list():
    db = get_db_connection()
    cursor = db.cursor()

    try:
        cursor.execute("SELECT name FROM template_table")
        templates = cursor.fetchall()

        if not templates:
            raise NotFoundError("Templates in database do clone or file doesnt exist")

        for row in templates:
            print(f"- Шаблоны: {row[0]}")

    finally:
        cursor.close()
        db.close()


def get_templates():
    db = get_db_connection()
    cursor = db.cursor()
    try:

        cursor.execute("""SELECT id, name FROM template_table""")
        templates_rows = cursor.fetchall()

        result_templates = list()

        for template_id, template_name in templates_rows:
            cursor.execute(
                """SELECT payment_type, value, description FROM payments_table WHERE template_id = ?""",
                (template_id,)
            )
            payments_rows = cursor.fetchall()

            payments_list = list()
            for payment_type, value, description in payments_rows:
                payments_list.append({
                    "__type__": payment_type,
                    "value": value,
                    "description": description
                })

            result_templates.append({
                "name": template_name,
                "payments": payments_list
            })

        return result_templates

    except sqlite3.Error as error:
        raise NotFoundError(f"Ошибка БД при чтении списка: {str(error)}")
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()


def delete_template(name: str):
    db = None
    cursor = None
    try:
        db = get_db_connection()
        cursor = db.cursor()

        with db:
            cursor.execute(
                """DELETE FROM payments_table WHERE template_id = (SELECT id FROM template_table WHERE name = ?)""",
                (name,)
            )
            cursor.execute("""DELETE FROM template_table WHERE name = ?""", (name,))

        return {"status": "success", "message": f"Template {name} deleted from SQL Database"}
    except sqlite3.Error as error:
        raise NotFoundError(f"Ошибка БД при удалении: {str(error)}")
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()
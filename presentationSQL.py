from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from decimal import Decimal
import sqlite3

from domain import APIValidator, execute_budget_simulation, InvalidTypeError
from storageSQL import packing_to_sql, template_from_sql, get_db_connection, init_db

app = FastAPI(title="Finlite API (SQL Version)")

init_db()

app.add_middleware(
    middleware_class=CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_index():
    return FileResponse("index.html")

@app.get("/api/templates")
async def get_templates():
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
        raise HTTPException(status_code=500, detail=f"Ошибка БД при чтении списка: {str(error)}")
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()


@app.post("/api/templates")
async def create_template(request: Request):
    try:
        raw_data = await request.json()
        validator = APIValidator(value=raw_data, target_type=dict)
        template_object = validator.to_template()

        packing_to_sql(template_object)
        return {"status": "success", "message": "Template saved to SQL Database"}
    except InvalidTypeError as error_type:
        raise HTTPException(status_code=400, detail=str(error_type))
    except Exception as error:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(error)}")


@app.post("/api/calculate")
async def calculate_budget(request: Request):
    try:
        raw_data = await request.json()
        template_name = raw_data.get("template_name")
        amount_raw = raw_data.get("amount")

        if not template_name or amount_raw is None:
            raise HTTPException(status_code=400, detail="Missing template name or amount")

        template = template_from_sql(template_name)
        initial_money = Decimal(str(amount_raw))

        calculation_result = execute_budget_simulation(template, initial_money)

        return {"status": "success", "result": calculation_result}
    except Exception as error_source:
        return {"status": "error", "message": f"Ошибка расчета: {str(error_source)}"}


@app.delete("/api/templates/{name}")
async def delete_template(name: str):
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
    except sqlite3.Error as http_error:
        raise HTTPException(status_code=500, detail=f"Ошибка БД при удалении: {str(http_error)}")
    finally:
        if cursor is not None:
            cursor.close()
        if db is not None:
            db.close()
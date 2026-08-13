from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from decimal import Decimal

from domain import APIValidator, execute_budget_simulation, InvalidTypeError
from storageSQL import packing_to_sql, template_from_sql, delete_template, init_db, get_templates, part_delete

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
async def show_templates():
    return get_templates()


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
async def delete_templates(name: str):
    return delete_template(name)

@app.delete("/api/templates/{name}")
async def delete_partly(name:str, index:int):
    return part_delete(name, index)
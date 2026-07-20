from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from decimal import Decimal

from domain import APIValidator, execute_budget_simulation, InvalidTypeError
from storage import packing_to_json, json_read, template_from_json

app = FastAPI(title="Finlite API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/templates")
async def get_templates():
    template_data = json_read()
    return template_data.get("templates", [])

@app.post("/api/templates")
async def create_template(request: Request):
    try:
        raw_data = await request.json()
        validator = APIValidator(value=raw_data, target_type=dict)
        template_object = validator.to_template()

        packing_to_json(template_object)
        return {"status": "success", "message": "Template saved"}
    except InvalidTypeError as error_type:
        raise HTTPException(status_code=400, detail=str(error_type))
    except Exception:
        raise HTTPException(status_code=500, detail=f"Internal error:")


@app.post("/api/calculate")
async def calculate_budget(request: Request):
    try:
        raw_data = await request.json()
        template_name = raw_data.get("template_name")
        amount_raw = raw_data.get("amount")

        if not template_name or amount_raw is None:
            raise HTTPException(status_code=400, detail="Missing template name or amount")

        template = template_from_json(template_name)
        initial_money = Decimal(str(amount_raw))

        calculation_result = execute_budget_simulation(template, initial_money)

        return {"status": "success", "result": calculation_result}
    except Exception as error_source:
        return {"status": "error", "message": f"Ошибка расчета: {str(error_source)}"}


@app.delete("/api/templates/{name}")
async def delete_template(name: str):
    try:
        data = json_read()
        updated_templates = [t for t in data.get("templates", []) if t.get("name") != name]
        data["templates"] = updated_templates

        import storage
        storage.json_write(data)
        return {"status": "success", "message": f"Template {name} deleted"}
    except Exception as http_error:
        raise HTTPException(status_code=500, detail=str(http_error))
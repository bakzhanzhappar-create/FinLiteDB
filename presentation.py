from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from decimal import Decimal

# Импортируем твои доменные классы и хранилище
from domain import ApiValidator, execute_budget_simulation, InvalidTypeError
from storage import packing_to_json, json_read, template_from_json

app = FastAPI(title="Finlite API")

# Разрешаем вебке слать CORS-запросы (Ctrl+F5 на фронте больше не нужен)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/templates")
async def get_templates():
    # Фронтенд ожидает список, берем из storage
    data = json_read()
    return data.get("templates", [])


@app.post("/api/templates")
async def create_template(request: Request):
    try:
        raw_data = await request.json()
        # Пропускаем через кастомный доменный валидатор вместо Pydantic
        validator = ApiValidator(value=raw_data, target_type=dict)
        template_object = validator.to_template()

        # Сохраняем в JSON через твой storage.py
        packing_to_json(template_object)
        return {"status": "success", "message": "Template saved"}
    except InvalidTypeError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {e}")


@app.get("/api/banks")
async def get_banks():
    data = json_read()
    banks = data.get("banks", [])
    # Фронт ждет поле current_scale, маппим его обратно из amount перед отдачей
    for bank in banks:
        bank["current_scale"] = bank.pop("amount", 0)
    return banks


@app.post("/api/banks")
async def create_bank(request: Request):
    try:
        raw_data = await request.json()
        validator = ApiValidator(value=raw_data, target_type=dict)
        bank_object = validator.to_bank()

        packing_to_json(bank_object)
        return {"status": "success", "message": "Bank opened"}
    except InvalidTypeError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/calculate")
async def calculate_budget(request: Request):
    try:
        raw_data = await request.json()
        tpl_name = raw_data.get("template_name")
        amount_raw = raw_data.get("amount")

        if not tpl_name or amount_raw is None:
            raise HTTPException(status_code=400, detail="Missing template name or amount")

        # Достаем шаблон из базы через твой storage.py
        template = template_from_json(tpl_name)
        initial_money = Decimal(str(amount_raw))

        # Запускаем расчет логики FIFO
        calculation_result = execute_budget_simulation(template, initial_money)

        return {"status": "success", "result": calculation_result}
    except Exception as e:
        return {"status": "error", "message": f"Ошибка расчета: {str(e)}"}


@app.delete("/api/templates/{name}")
async def delete_template(name: str):
    try:
        data = json_read()
        # Фильтруем список, оставляя все шаблоны КРОМЕ удаляемого
        updated_templates = [t for t in data.get("templates", []) if t.get("name") != name]
        data["templates"] = updated_templates

        # Перезаписываем обновленный словарь обратно в файл через твой storage.py
        import storage
        storage.json_write(data)
        return {"status": "success", "message": f"Template {name} deleted"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/banks/{name:path}")
async def delete_bank(name: str):
    try:
        # На всякий случай декодируем имя, если прилетели url-символы
        import urllib.parse
        clean_name = urllib.parse.unquote(name).strip()

        data = json_read()
        # Фильтруем список, убирая пробелы при сравнении
        updated_banks = [b for b in data.get("banks", []) if b.get("name", "").strip() != clean_name]
        data["banks"] = updated_banks

        import storage
        storage.json_write(data)
        return {"status": "success", "message": f"Bank {clean_name} closed"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
import json
import os
from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.responses import JSONResponse

from core import InvalidPaymentError, InvalidTypeError
from storage import NotFoundError
from main import FinanceOrchestrator

app = FastAPI(title="Finlite API")


# =====================================================================
# 🛠️ ХАРДКОРНЫЙ КАСТОМНЫЙ CORS-ФИЛЬТР (Датчик + Принудительный пропуск)
# =====================================================================
@app.middleware("http")
async def force_cors_and_diagnostic(request: Request, call_next):
    origin = request.headers.get("origin", "*")
    method = request.method
    path = request.url.path

    print(f"\n[📡 ДАТЧИК] Запрос: {method} {path} | Откуда: {origin}")

    # Если браузер прислал проверочный preflight-запрос (OPTIONS)
    if method == "OPTIONS":
        print(f"   [⚙️ OPTIONS] Ловим preflight-запрос. Насильно одобряем.")
        response = Response(status_code=204)
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "*"
        response.headers["Access-Control-Max-Age"] = "86400"
        return response

    # Для обычных GET/POST запросов
    response = await call_next(request)

    # Жестко вшиваем заголовки в ответ, игнорируя стандартные настройки
    response.headers["Access-Control-Allow-Origin"] = origin
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"

    print(f"[📬 ОТВЕТ] Статус: {response.status_code}")
    return response


# Инициализация оркестратора
orchestrator = FinanceOrchestrator()

TEMPLATES_FILE = "templates.json"
BANKS_FILE = "banks.json"


# =====================================================================
# GET-ЭНДПОИНТЫ: Чтение данных
# =====================================================================

@app.get("/api/templates")
async def web_get_templates():
    try:
        if not os.path.exists(TEMPLATES_FILE):
            return []

        with open(TEMPLATES_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            templates_list = []
            for name, content in data.items():
                if isinstance(content, dict):
                    payments = content.get("payments", [])
                elif isinstance(content, list):
                    payments = content
                else:
                    payments = []

                templates_list.append({
                    "name": name,
                    "payments": payments
                })
            return templates_list

        return []
    except Exception as e:
        print(f"❌ Ошибка парсинга шаблонов: {e}")
        return []


@app.get("/api/banks")
async def web_get_banks():
    try:
        if not os.path.exists(BANKS_FILE):
            return []

        with open(BANKS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, list):
            return data

        if isinstance(data, dict):
            banks_list = []
            for name, content in data.items():
                if isinstance(content, dict):
                    banks_list.append({
                        "name": name,
                        "target_scale": content.get("target_scale", 0),
                        "current_scale": content.get("current_scale", 0),
                        "description": content.get("description", "")
                    })
                else:
                    banks_list.append({
                        "name": name,
                        "target_scale": 0,
                        "current_scale": content,
                        "description": ""
                    })
            return banks_list

        return []
    except Exception as e:
        print(f"❌ Ошибка парсинга банков: {e}")
        return []


# =====================================================================
# POST-ЭНДПОИНТЫ: Действия (Создание и Расчеты)
# =====================================================================

@app.post("/api/templates")
async def web_create_template(payload: dict):
    try:
        new_template = orchestrator.create_template(payload)
        return {"status": "success", "message": f"Шаблон '{new_template.name}' сохранен"}
    except (InvalidPaymentError, InvalidTypeError) as e:
        return JSONResponse(status_code=400, content={"status": "error", "message": str(e)})


@app.post("/api/banks")
async def web_create_bank(payload: dict):
    try:
        new_bank = orchestrator.create_bank(payload)
        return {"status": "success", "message": f"Банк '{new_bank.name}' открыт"}
    except (InvalidPaymentError, InvalidTypeError) as e:
        return JSONResponse(status_code=400, content={"status": "error", "message": str(e)})


@app.post("/api/calculate")
async def web_calculate(payload: dict):
    try:
        template_name = payload.get("template_name")
        amount = payload.get("amount")

        result = orchestrator.execute_calculation(template_name, amount)
        return {"status": "success", "result": result}
    except NotFoundError as e:
        return JSONResponse(status_code=404, content={"status": "error", "message": str(e)})
    except (InvalidPaymentError, InvalidTypeError) as e:
        return JSONResponse(status_code=400, content={"status": "error", "message": str(e)})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
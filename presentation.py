# presentation.py
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware  # Импортируем CORS

from core import InvalidPaymentError, InvalidTypeError
from storage import NotFoundError
from main import FinanceOrchestrator

app = FastAPI(title="Finlite API")

# Включаем CORS-прослойку
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],             # Разрешает запросы с любых адресов и портов
    allow_credentials=True,
    allow_methods=["*"],             # Разрешает POST, GET, OPTIONS и т.д.
    allow_headers=["*"],             # Разрешает любые заголовки (Content-Type и т.д.)
)

orchestrator = FinanceOrchestrator()


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
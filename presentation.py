from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
# Импортируем схемы и движок вычислений из main.py
from main import (
    TemplateItemIn, BankCreateIn, TemplateExecIn, BankDepositIn,
    calculate_template
)

app = FastAPI()

# Разрешаем CORS, чтобы фронтенд из chernovik.html мог делать запросы
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Мок-база данных (В будущем этот блок улетит в storage.py)
DB = {
    "templates": {
        "Стипендия": [
            {"name": "За проезд", "type": "fix", "value": 1320},
            {"name": "На все про все", "type": "fix", "value": 28000},
            {"name": "Самоналог", "type": "percent", "value": 30}
        ]
    },
    "banks": [
        {
            "name": "Lada",
            "target_scale": 45000,
            "current_amount": 7633,
            "description": "Once i have a dream that one day ill move w niggas to diff cities"
        }
    ]
}


@app.get("/api/dashboard")
def get_dashboard_data():
    """Отдает всю базу одной пачкой для отрисовки интерфейса при загрузке"""
    return DB


@app.post("/api/templates/add")
def add_item_to_template(payload: TemplateItemIn):
    """Добавляет новое правило распределения (Fix/% элемент) в выбранный шаблон"""
    t_name = payload.template_name

    if t_name not in DB["templates"]:
        DB["templates"][t_name] = []

    DB["templates"][t_name].append({
        "name": payload.item_name,
        "type": payload.type,
        "value": payload.value
    })
    return {"status": "success", "message": f"Элемент добавлен в шаблон {t_name}"}


@app.post("/api/banks/create")
def create_new_bank(payload: BankCreateIn):
    """Открывает новый накопительный счет (Банку)"""
    # Проверяем уникальность имени, чтобы не затереть существующую цель
    if any(b["name"].lower() == payload.name.lower() for b in DB["banks"]):
        raise HTTPException(status_code=400, detail="Банк с таким именем уже существует")

    DB["banks"].append({
        "name": payload.name,
        "target_scale": payload.target_scale,
        "current_amount": 0.0,
        "description": payload.description
    })
    return {"status": "success"}


@app.post("/api/templates/execute")
def execute_distribution(payload: TemplateExecIn):
    """Прогоняет сумму по формуле выбранного шаблона"""
    t_name = payload.template_name
    if t_name not in DB["templates"]:
        raise HTTPException(status_code=404, detail="Указанный шаблон не найден")

    items = DB["templates"][t_name]
    result = calculate_template(payload.amount, items)

    return {
        "initial_amount": payload.amount,
        "result_amount": result
    }


@app.post("/api/banks/deposit")
def deposit_to_bank(payload: BankDepositIn):
    """Пополняет баланс конкретной копилки"""
    for bank in DB["banks"]:
        if bank["name"].lower() == payload.bank_name.lower():
            bank["current_amount"] += payload.amount
            return bank

    raise HTTPException(status_code=404, detail="Указанная копилка не найдена")
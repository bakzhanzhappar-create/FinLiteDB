#обязанности у этого модуля:
#Объединить с auth.py, app.py, dealer_input, reader.py в presentation.py
#Строго IO и веб интерфейс функционал
#Presentation.py

# -*- coding: utf-8 -*-
"""
Streamlit-интерфейс FinLiteDB.
Бэкенд: auth.py, logic.py, storage.py, dealer_input.py, reader (логика).
"""
import json
import streamlit as st
import logic
import storage
import dealer_input

#чтение. To storage_test.py
def get_user_db(username):
    """Читает JSON пользователя. Возвращает dict или None."""
    filename = f"{username}.json"
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None

#To core.py
#получаем словарь без копилки
def get_templates(username):
    """Список имён шаблонов (без piggybanks)."""
    db = get_user_db(username)
    if not db:
        return []
#проверка в одну строку ищем не является ли k "piggybanks"
    return [k for k in db.keys() if k != "piggybanks"]

#To core.py from app.py
#получаем список копилок по ключу функции get()
def get_piggybanks(username):
    """Словарь копилок пользователя."""
    db = get_user_db(username)
    if not db:
        return {}
    return db.get("piggybanks", {})

#запись. To storage_test.py from app.py
def create_profile(username):
    """Создаёт файл профиля с базовой структурой."""
    filename = f"{username}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump({"piggybanks": {}}, f, indent=4)
    return True

#запись. To storage_test.py from app.py
def write_user_db(username, data):
    """Записывает данные в JSON пользователя."""
    filename = f"{username}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

#To core.py from app.py
def delete_template(username, template_name):
    """Удаляет шаблон по имени. Возвращает True при успехе."""
    db = get_user_db(username)
    if not db or template_name not in db or template_name == "piggybanks":
        return False
    del db[template_name]
    write_user_db(username, db)
    return True

#To core.py from app.py
def delete_piggybank(username, goal_name):
    """Удаляет копилку по имени. Возвращает True при успехе."""
    db = get_user_db(username)
    if not db: return False
    pigs = db.get("piggybanks", {})
    if goal_name not in pigs: return False
    del pigs[goal_name]
    db["piggybanks"] = pigs
    write_user_db(username, db)
    return True

#To presentation.py from app.py
# --- Session state ---
if "user" not in st.session_state:
    st.session_state.user = None
if "fifo_remains" not in st.session_state:
    st.session_state.fifo_remains = None

# --- Sidebar: авторизация ---
st.sidebar.title("Вход в систему")
login = st.sidebar.text_input("Логин", value="", key="login").strip().lower()
if not login:
    login = "guest"

db = get_user_db(login)
if db is not None:
    st.session_state.user = login
    st.sidebar.success(f"Привет, {login}!")
else:
    st.session_state.user = None
    st.sidebar.warning(f"Профиль '{login}' не найден.")
    if st.sidebar.button("Создать профиль"):
        create_profile(login)
        st.session_state.user = login
        st.sidebar.success("Профиль создан. Обновите страницу или введите логин снова.")
        st.rerun()

# --- Основной контент только для авторизованного пользователя ---
if st.session_state.user is None:
    st.info("Введите логин и нажмите «Создать профиль», если профиля ещё нет.")
    st.stop()

username = st.session_state.user

# --- Вкладки ---
tab_fifo, tab_templates, tab_piggy, tab_delete = st.tabs([
    "💰 Расчет FIFO", "📊 Мои Шаблоны", "🐷 Копилка", "🗑️ Удаление"
])

# ---------- Вкладка: Расчет FIFO ----------
with tab_fifo:
    st.subheader("Расчет FIFO")
    templates = get_templates(username)
    if not templates:
        st.warning("Сначала создайте шаблоны во вкладке «Мои Шаблоны».")
    else:
        amount = st.number_input("Сумма", min_value=0.0, value=0.0, step=10.0, key="fifo_amount")
        template_name = st.selectbox("Шаблон", options=templates, key="fifo_template")
        if st.button("Рассчитать", key="btn_fifo"):
#Здесь вызывают run_fifo  из logic.py
            balance, history, fail_idx = logic.run_fifo(amount, username, template_name=template_name)
            for line in history:
                st.write(line)
            if fail_idx is not None:
                st.error(f"ВНИМАНИЕ: Не хватило! Начиная с правила номер {fail_idx}")
            st.metric("Итоговый остаток", f"{balance:.2f}")
            if balance < 0:
                st.error(f"Итоговый остаток: {balance:.2f}")
            elif history:
                st.session_state.fifo_remains = balance

# ---------- Вкладка: Мои Шаблоны ----------
with tab_templates:
    st.subheader("Мои Шаблоны")
    db = get_user_db(username)
    templates_dict = {k: v for k, v in (db or {}).items() if k != "piggybanks"}
    if not templates_dict:
        st.write("Шаблонов пока нет.")
    else:
        for name, rules in templates_dict.items():
            # Новый формат: один список правил в порядке FIFO
            if isinstance(rules, list) and rules and isinstance(rules[0], dict) and rules[0].get("type") in ("f", "p"):
                total = len(rules)
                with st.expander(f" {name} (правил: {total})"):
                    for i, r in enumerate(rules):
                        if r.get("type") == "f":
                            st.write(f"{i+1}. Фикс: {r.get('val', 0)} ({r.get('desc', '')})")
                        else:
                            st.write(f"{i+1}. Проц: {r.get('val', 0)}% ({r.get('desc', '')})")
            else:
                # Старый формат [fixes, percs]
                f_list, p_list = rules
                act_f = len([x for x in f_list if x[0] > 0])
                act_p = len([x for x in p_list if x[0] > 0])
                with st.expander(f" {name} (фиксов: {act_f}, проц: {act_p})"):
                    for i in range(len(f_list)):
                        if f_list[i][0] > 0:
                            st.write(f"Фикс: {f_list[i][0]} ({f_list[i][1]})")
                        if p_list[i][0] > 0:
                            st.write(f"Проц: {p_list[i][0]}% ({p_list[i][1]})")

    st.divider()
    st.subheader("Создать шаблон")
    new_name = st.text_input("Имя шаблона", key="new_tpl_name")
    if "_rules" not in st.session_state:
        st.session_state._rules = []

    st.write("Правила в порядке добавления (FIFO): сначала добавил — сначала применяется.")
    col1, col2 = st.columns(2)
    with col1:
#Переменные фикс
        fix_val = st.number_input("Фикс — сумма", min_value=0, value=0, key="fix_val")
        fix_desc = st.text_input("Фикс — описание", key="fix_desc")
        if st.button("Добавить фикс", key="add_fix"):
            st.session_state._rules.append({"type": "f", "val": fix_val, "desc": fix_desc or "пусто"})
            st.rerun()
    with col2:
# Переменные проц
        perc_val = st.number_input("Процент (0–100)", min_value=0, max_value=100, value=0, key="perc_val")
        perc_desc = st.text_input("Процент — описание", key="perc_desc")
        if st.button("Добавить процент", key="add_perc"):
            st.session_state._rules.append({"type": "p", "val": perc_val, "desc": perc_desc or "пусто"})
            st.rerun()

    st.write("Порядок правил (как добавляли):")
#Цикл где отображают записанные переменые
    for i, r in enumerate(st.session_state._rules):
        if r.get("type") == "f":
            st.caption(f"{i+1}. Фикс: {r.get('val', 0)} — {r.get('desc', '')}")
        else:
            st.caption(f"{i+1}. Проц: {r.get('val', 0)}% — {r.get('desc', '')}")

    if st.button("Сохранить шаблон", key="save_tpl"):
        if not new_name.strip():
            st.error("Введите имя шаблона.")
        elif not st.session_state._rules:
            st.error("Добавьте хотя бы одно правило (фикс или процент).")
        else:
            ok, err = dealer_input.save_template(username, new_name.strip(), list(st.session_state._rules))
            if ok:
                st.success(f"Шаблон «{new_name}» сохранён.")
                st.session_state._rules = []
                st.rerun()
            else:
                st.error(err or "Ошибка сохранения.")

# ---------- Вкладка: Копилка ----------
with tab_piggy:
    st.subheader("Копилка")
    banks = get_piggybanks(username)
    if not banks:
        st.write("Копилок пока нет. Создайте ее ниже.")
    else:
        for goal_name, data in banks.items():
            target = data.get("target", 1)
            current = data.get("current", 0)
            link = data.get("link", "")
            pct = min(100.0, (current / target * 100) if target else 0)
            st.write(f"**{goal_name}** — {current:.0f} / {target:.0f}")
            st.progress(pct / 100.0)
            if link:
                st.caption(link)
        st.divider()

    # Перевести остаток из FIFO в копилку
    remains = st.session_state.get("fifo_remains")
    if remains is not None and remains > 0 and banks:
        st.write("Остаток после расчёта FIFO можно закинуть в копилку:")
        goal = st.selectbox("В какую копилку?", options=list(banks.keys()), key="piggy_goal")
        if st.button("Закинуть остаток", key="btn_deposit"):
            bank = storage.PiggyBank(username)
            if bank.deposit(remains, goal_name=goal):
                st.session_state.fifo_remains = None
                st.success(f"Зачислено {remains:.2f} в «{goal}».")
                st.rerun()
            else:
                st.error("Не удалось зачислить.")
    elif remains is not None and remains > 0 and not banks:
        st.info("Создайте копилку ниже, чтобы закинуть остаток.")

    st.subheader("Создать копилку")
    g_name = st.text_input("На что копим?", key="goal_name")
    g_target = st.number_input("Целевая сумма", min_value=0.0, value=0.0, key="goal_target")
    g_link = st.text_input("Описание (необязательно)", key="goal_link")
    if st.button("Создать копилку", key="btn_create_goal"):
        if g_name.strip() and g_target > 0:
            bank = storage.PiggyBank(username)
            bank.create_goal(name=g_name.strip(), target=g_target, link=g_link or "")
            st.success(f"Копилка «{g_name}» создана.")
            st.rerun()
        else:
            st.error("Укажите название и целевую сумму.")

# ---------- Вкладка: Удаление ----------
with tab_delete:
    st.subheader("Удалить шаблон")
    search_tpl = st.text_input("Поиск по названию шаблона", key="search_tpl", placeholder="Введите часть названия...")
    templates_all = get_templates(username)
    if search_tpl.strip():
        templates_filtered = [n for n in templates_all if search_tpl.strip().lower() in n.lower()]
    else:
        templates_filtered = templates_all
    if not templates_filtered:
        st.caption("Нет шаблонов" + (" по запросу." if search_tpl.strip() else "."))
    else:
        for name in templates_filtered:
            col1, col2 = st.columns([3, 1])
            with col1:
                st.write(f" **{name}**")
            with col2:
                if st.button("Удалить", key=f"del_tpl_{name}"):
                    if delete_template(username, name):
                        st.success(f"Шаблон «{name}» удалён.")
                        st.rerun()
                    else:
                        st.error("Не удалось удалить.")

    st.divider()
    st.subheader("Удалить копилку")
    search_pig = st.text_input("Поиск по названию копилки", key="search_pig", placeholder="Введите часть названия...")
    banks = get_piggybanks(username)
    bank_names = list(banks.keys())
    if search_pig.strip():
        banks_filtered = [n for n in bank_names if search_pig.strip().lower() in n.lower()]
    else:
        banks_filtered = bank_names
    if not banks_filtered:
        st.caption("Нет копилок" + (" по запросу." if search_pig.strip() else "."))
    else:
        for name in banks_filtered:
            col1, col2 = st.columns([3, 1])
            with col1:
                data = banks[name]
                st.write(f" **{name}** — {data.get('current', 0):.0f} / {data.get('target', 0):.0f}")
            with col2:
                if st.button("Удалить", key=f"del_pig_{name}"):
                    if delete_piggybank(username, name):
                        st.success(f"Копилка «{name}» удалена.")
                        st.rerun()
                    else:
                        st.error("Не удалось удалить.")

# -*- coding: utf-8 -*-
"""Streamlit FinLiteDB: auth, logic, storage, dealer_input, user_records."""
import json
import random

import streamlit as st

import dealer_input
import logic
import storage
import user_records

# Freedom Bank (KZ) — акцент
FB_GREEN = "#4FAF3B"
FB_GREEN_DARK = "#1F5019"

# Светлая тема: контраст страница vs поля, читаемые подписи
L_PAGE_BG = "#ECEFEA"
L_SURFACE = "#FFFFFF"
L_SIDEBAR = "#E2E8DE"
L_TEXT = "#0A1F08"
L_TEXT_MUTED = "#3D5A38"
L_BORDER_STRONG = "#1F5019"
L_BORDER_FIELD = "#2D6B26"
L_INPUT_BG = "#FFFFFF"
L_INPUT_FOCUS = "#4FAF3B"
L_THEME_TOGGLE_LABEL = "#021608"

# Тёмная тема: нейтральный тёмный UI + зелёный только акцент
D_PAGE_BG = "#0D1117"
D_SURFACE = "#161B22"
D_ELEVATED = "#1C232D"
D_BORDER = "#3D4A5C"
D_TEXT = "#F0F4F8"
D_TEXT_MUTED = "#9BA8B8"
D_INPUT_BG = "#0D1219"
D_INPUT_BORDER = "#5C6B7E"
D_ACCENT = FB_GREEN


def _parse_amount(s, default=None):
    s = (s or "").strip().replace(",", ".")
    if not s:
        return default
    try:
        return int(round(float(s)))
    except ValueError:
        return None


def _parse_float_amount(s, default=None):
    s = (s or "").strip().replace(",", ".")
    if not s:
        return default
    try:
        return float(s)
    except ValueError:
        return None


def _theme_css_main(is_dark: bool) -> str:
    if is_dark:
        return _css_dark_theme()
    return _css_light_theme()


def _css_light_theme() -> str:
    g, gd = FB_GREEN, FB_GREEN_DARK
    return f"""
    <style>
    .stApp {{
        background-color: {L_PAGE_BG} !important;
        color: {L_TEXT} !important;
    }}
    section[data-testid="stMain"] > div {{
        background-color: {L_PAGE_BG} !important;
    }}
    div[data-testid="stSidebar"] {{
        background-color: {L_SIDEBAR} !important;
        border-right: 2px solid {L_BORDER_STRONG} !important;
    }}
    div[data-testid="stSidebar"] p, div[data-testid="stSidebar"] span, div[data-testid="stSidebar"] label {{
        color: {L_TEXT} !important;
    }}
    /* Подписи к виджетам — жирнее и темнее */
    .stTextInput label p, .stSelectbox label p, .stNumberInput label p,
    .stMultiSelect label p, .stTextArea label p {{
        color: {L_TEXT} !important;
        font-weight: 600 !important;
        font-size: 0.95rem !important;
    }}
    /* Поля ввода: белый блок на сероватом фоне, явная рамка */
    div[data-testid="stTextInput"] [data-baseweb="input"],
    div[data-testid="stNumberInput"] [data-baseweb="input"] {{
        background-color: {L_INPUT_BG} !important;
        border: 2px solid {L_BORDER_FIELD} !important;
        border-radius: 8px !important;
    }}
    div[data-testid="stTextInput"] [data-baseweb="input"] input,
    div[data-testid="stNumberInput"] [data-baseweb="input"] input {{
        background-color: {L_INPUT_BG} !important;
        color: {L_TEXT} !important;
        font-weight: 500 !important;
        -webkit-text-fill-color: {L_TEXT} !important;
    }}
    div[data-testid="stTextInput"] [data-baseweb="input"] input::placeholder,
    div[data-testid="stNumberInput"] [data-baseweb="input"] input::placeholder {{
        color: {L_TEXT_MUTED} !important;
        opacity: 1 !important;
    }}
    div[data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
    div[data-testid="stNumberInput"] [data-baseweb="input"]:focus-within {{
        border-color: {L_INPUT_FOCUS} !important;
        box-shadow: 0 0 0 1px {L_INPUT_FOCUS} !important;
    }}
    /* Selectbox */
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div {{
        background-color: {L_INPUT_BG} !important;
        border: 2px solid {L_BORDER_FIELD} !important;
        border-radius: 8px !important;
        color: {L_TEXT} !important;
    }}
    div[data-testid="stSelectbox"] [data-baseweb="select"] * {{
        color: {L_TEXT} !important;
    }}
    /* Вкладки */
    div[data-testid="stTabs"] button {{
        color: {L_TEXT_MUTED} !important;
    }}
    div[data-testid="stTabs"] button[aria-selected="true"] {{
        color: {gd} !important;
        border-bottom: 3px solid {g} !important;
        font-weight: 700 !important;
    }}
    /* Карточки */
    div[data-testid="stMetric"] {{
        background-color: {L_SURFACE} !important;
        border: 2px solid {L_BORDER_FIELD} !important;
        border-radius: 10px;
        padding: 0.5rem 0.75rem;
    }}
    div[data-testid="stExpander"] {{
        border: 2px solid {L_BORDER_FIELD} !important;
        border-radius: 10px;
        background-color: {L_SURFACE} !important;
    }}
    div[data-testid="stExpander"] summary {{
        color: {L_TEXT} !important;
        font-weight: 600 !important;
    }}
    .stProgress > div > div > div {{
        background-color: {g} !important;
    }}
    /* Кнопки secondary / default — видимая обводка */
    div.stButton > button {{
        border: 2px solid {L_BORDER_FIELD} !important;
        color: {gd} !important;
        font-weight: 600 !important;
    }}
    div.stButton > button[kind="primary"] {{
        background-color: {g} !important;
        border-color: {g} !important;
        color: #FFFFFF !important;
    }}
    /* Подпись «Тёмная тема» — контраст к фону шапки */
    div[data-testid="stToggle"] label p,
    div[data-testid="stToggle"] [data-testid="stWidgetLabel"] p {{
        color: {L_THEME_TOGGLE_LABEL} !important;
        font-weight: 800 !important;
        font-size: 0.98rem !important;
    }}
    </style>
    """


def _css_dark_theme() -> str:
    """Нейтральный тёмный UI + зелёный акцент. Охватывает вход, сайдбар, шапку, алерты."""
    a = D_ACCENT
    return f"""
    <style>
    html, body, [data-testid="stAppViewContainer"] {{
        background-color: {D_PAGE_BG} !important;
    }}
    .stApp {{
        background-color: {D_PAGE_BG} !important;
        color: {D_TEXT} !important;
    }}
    /* Верхняя панель Streamlit */
    header[data-testid="stHeader"] {{
        background-color: {D_PAGE_BG} !important;
        border-bottom: 1px solid {D_BORDER} !important;
    }}
    div[data-testid="stToolbar"] {{
        background-color: {D_PAGE_BG} !important;
    }}
    div[data-testid="stDecoration"] {{
        background-image: none !important;
        background-color: {D_PAGE_BG} !important;
    }}
    section[data-testid="stMain"] > div {{
        background-color: {D_PAGE_BG} !important;
    }}
    div[data-testid="stMain"] {{
        background-color: {D_PAGE_BG} !important;
    }}
    /* Сайдбар целиком (в т.ч. экран «Вход в систему») */
    section[data-testid="stSidebar"] {{
        background-color: {D_SURFACE} !important;
        border-right: 1px solid {D_BORDER} !important;
    }}
    div[data-testid="stSidebar"] {{
        background-color: {D_SURFACE} !important;
        border-right: 1px solid {D_BORDER} !important;
    }}
    div[data-testid="stSidebarContent"] {{
        background-color: {D_SURFACE} !important;
    }}
    div[data-testid="stSidebar"] h1,
    div[data-testid="stSidebar"] h2,
    div[data-testid="stSidebar"] h3 {{
        color: {D_TEXT} !important;
    }}
    div[data-testid="stSidebar"] p, div[data-testid="stSidebar"] span, div[data-testid="stSidebar"] label {{
        color: {D_TEXT} !important;
    }}
    /* Текст в основном контенте */
    .main h1, .main h2, .main h3, .main p, .main span, .main li {{
        color: {D_TEXT} !important;
    }}
    .stTextInput label p, .stSelectbox label p, .stNumberInput label p,
    .stMultiSelect label p, .stTextArea label p {{
        color: {D_TEXT} !important;
        font-weight: 600 !important;
    }}
    /* Поля ввода */
    div[data-testid="stTextInput"] [data-baseweb="input"],
    div[data-testid="stNumberInput"] [data-baseweb="input"] {{
        background-color: {D_INPUT_BG} !important;
        border: 2px solid {D_INPUT_BORDER} !important;
        border-radius: 8px !important;
    }}
    div[data-testid="stTextInput"] [data-baseweb="input"] input,
    div[data-testid="stNumberInput"] [data-baseweb="input"] input {{
        background-color: {D_INPUT_BG} !important;
        color: {D_TEXT} !important;
        -webkit-text-fill-color: {D_TEXT} !important;
    }}
    div[data-testid="stTextInput"] [data-baseweb="input"] input::placeholder {{
        color: {D_TEXT_MUTED} !important;
        opacity: 1 !important;
    }}
    div[data-testid="stTextInput"] [data-baseweb="input"]:focus-within,
    div[data-testid="stNumberInput"] [data-baseweb="input"]:focus-within {{
        border-color: {a} !important;
        box-shadow: 0 0 0 1px {a} !important;
    }}
    div[data-testid="stSelectbox"] [data-baseweb="select"] > div {{
        background-color: {D_INPUT_BG} !important;
        border: 2px solid {D_INPUT_BORDER} !important;
        border-radius: 8px !important;
        color: {D_TEXT} !important;
    }}
    /* Вкладки */
    div[data-testid="stTabs"] button {{
        color: {D_TEXT_MUTED} !important;
    }}
    div[data-testid="stTabs"] button[aria-selected="true"] {{
        color: {D_TEXT} !important;
        border-bottom: 3px solid {a} !important;
        font-weight: 700 !important;
    }}
    /* Метрики / expander */
    div[data-testid="stMetric"] {{
        background-color: {D_ELEVATED} !important;
        border: 1px solid {D_BORDER} !important;
        border-radius: 10px;
    }}
    div[data-testid="stMetric"] label, div[data-testid="stMetric"] [data-testid="stMarkdownContainer"] p {{
        color: {D_TEXT_MUTED} !important;
    }}
    div[data-testid="stMetric"] [data-testid="stMetricValue"] > div {{
        color: {D_TEXT} !important;
    }}
    div[data-testid="stExpander"] {{
        border: 1px solid {D_BORDER} !important;
        border-radius: 10px;
        background-color: {D_ELEVATED} !important;
    }}
    div[data-testid="stExpander"] summary {{
        color: {D_TEXT} !important;
    }}
    .stProgress > div > div > div {{
        background-color: {a} !important;
    }}
    /* Подпись переключателя темы — ярче основного текста */
    div[data-testid="stToggle"] label p,
    div[data-testid="stToggle"] [data-testid="stWidgetLabel"] p {{
        color: #F8FAFC !important;
        font-weight: 800 !important;
    }}
    div.stButton > button {{
        border: 1px solid {D_BORDER} !important;
        color: {D_TEXT} !important;
        background-color: {D_SURFACE} !important;
    }}
    div.stButton > button[kind="primary"] {{
        background-color: {a} !important;
        border-color: {a} !important;
        color: #0D1117 !important;
        font-weight: 700 !important;
    }}
    /* st.info / success / warning / error — тёмная панель вместо светлого всплывающего */
    div[data-testid="stAlert"] {{
        background-color: {D_ELEVATED} !important;
        color: {D_TEXT} !important;
        border: 1px solid {D_BORDER} !important;
        border-left-width: 4px !important;
        border-left-color: {a} !important;
    }}
    div[data-testid="stAlert"] p,
    div[data-testid="stAlert"] span,
    div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] {{
        color: {D_TEXT} !important;
    }}
    /* Контейнер основной колонки на экране входа */
    .block-container {{
        background-color: transparent !important;
        padding-top: 1rem !important;
    }}
    </style>
    """


def get_user_db(username):
    filename = f"{username}.json"
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return None


def get_templates(username):
    db = get_user_db(username)
    if not db:
        return []
    return [k for k in db.keys() if k != "piggybanks"]


def get_piggybanks(username):
    db = get_user_db(username)
    if not db:
        return {}
    return db.get("piggybanks", {})


def create_profile(username):
    filename = f"{username}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump({"piggybanks": {}}, f, indent=4)
    return True


def write_user_db(username, data):
    filename = f"{username}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def delete_template(username, template_name):
    db = get_user_db(username)
    if not db or template_name not in db or template_name == "piggybanks":
        return False
    del db[template_name]
    write_user_db(username, db)
    return True


def delete_piggybank(username, goal_name):
    db = get_user_db(username)
    if not db:
        return False
    pigs = db.get("piggybanks", {})
    if goal_name not in pigs:
        return False
    del pigs[goal_name]
    db["piggybanks"] = pigs
    write_user_db(username, db)
    return True


st.set_page_config(page_title="FinLiteDB", layout="wide")

if "user" not in st.session_state:
    st.session_state.user = None
if "fifo_remains" not in st.session_state:
    st.session_state.fifo_remains = None

st.sidebar.title("Вход в систему")
_login_field = st.sidebar.text_input("Логин", value="", key="login").strip().lower()
login = _login_field if _login_field else "guest"

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
        st.sidebar.success("Профиль создан.")
        st.rerun()

# Одна тема на весь экран: до входа берём prefs по введённому логину (как у baga — сразу тёмный сайдбар)
if st.session_state.user is not None:
    _u = st.session_state.user
    if st.session_state.get("_prefs_user") != _u:
        _th = user_records.load_ui_prefs(_u).get("theme", "light")
        st.session_state.ui_theme = _th if _th in ("light", "dark") else "light"
        st.session_state._prefs_user = _u
    _effective_dark = st.session_state.ui_theme == "dark"
else:
    _th_login = user_records.load_ui_prefs(login).get("theme", "light")
    _effective_dark = _th_login == "dark"

st.markdown(_theme_css_main(_effective_dark), unsafe_allow_html=True)

if st.session_state.user is None:
    st.info("Введите логин и при необходимости создайте профиль.")
    st.stop()

username = st.session_state.user

hdr_left, hdr_mid, hdr_right = st.columns([3, 5, 3])
with hdr_left:
    st.markdown("### FinLiteDB")
with hdr_mid:
    pass
with hdr_right:
    want_dark = st.toggle(
        "🌙 Тёмная тема",
        value=st.session_state.ui_theme == "dark",
        key=f"ui_dark_{username}",
        help="Сохраняется отдельно для каждого логина (файл в records/)",
    )
if want_dark != (st.session_state.ui_theme == "dark"):
    st.session_state.ui_theme = "dark" if want_dark else "light"
    user_records.save_ui_theme(username, st.session_state.ui_theme)
    st.rerun()

tab_fifo, tab_templates, tab_piggy, tab_history, tab_delete = st.tabs(
    ["💰 Расчет FIFO", "📊 Мои Шаблоны", "🐷 Копилка", "📜 История", "🗑️ Удаление"]
)

with tab_fifo:
    st.subheader("Расчет FIFO")
    templates = get_templates(username)
    if not templates:
        st.warning("Сначала создайте шаблоны во вкладке «Мои Шаблоны».")
    else:
        fifo_amt_s = st.text_input("Сумма", key="fifo_amount_str")
        template_name = st.selectbox("Шаблон", options=templates, key="fifo_template")
        if st.button("Рассчитать", key="btn_fifo"):
            amount = _parse_float_amount(fifo_amt_s, 0.0)
            if amount is None or amount < 0:
                st.error("Введите корректную сумму (число).")
            else:
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

with tab_templates:
    st.subheader("Мои Шаблоны")
    db = get_user_db(username)
    templates_dict = {k: v for k, v in (db or {}).items() if k != "piggybanks"}
    if not templates_dict:
        st.write("Шаблонов пока нет.")
    else:
        for name, rules in templates_dict.items():
            if isinstance(rules, list) and rules and isinstance(rules[0], dict) and rules[0].get("type") in ("f", "p"):
                total = len(rules)
                with st.expander(f"📄 {name} (правил: {total})"):
                    for i, r in enumerate(rules):
                        if r.get("type") == "f":
                            st.write(f"{i+1}. Фикс: {r.get('val', 0)} ({r.get('desc', '')})")
                        else:
                            st.write(f"{i+1}. Проц: {r.get('val', 0)}% ({r.get('desc', '')})")
            else:
                f_list, p_list = rules
                act_f = len([x for x in f_list if x[0] > 0])
                act_p = len([x for x in p_list if x[0] > 0])
                with st.expander(f"📄 {name} (фиксов: {act_f}, проц: {act_p})"):
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

    st.caption("Порядок FIFO: как добавили правила — так они и применяются.")
    col1, col2 = st.columns(2)
    with col1:
        fix_s = st.text_input("Фикс — сумма", key="fix_val_str")
        fix_desc = st.text_input("Фикс — описание", key="fix_desc")
        if st.button("Добавить фикс", key="add_fix"):
            fv = _parse_amount(fix_s, None)
            if fv is None:
                st.error("Введите число для фикса.")
            elif fv < 0:
                st.error("Сумма не может быть отрицательной.")
            else:
                st.session_state._rules.append({"type": "f", "val": fv, "desc": fix_desc or "пусто"})
                st.rerun()
    with col2:
        # Кубик: нельзя писать в ключ виджета после его создания — ставим значение ДО text_input.
        if "_perc_roll_value" in st.session_state:
            _pv = st.session_state.pop("_perc_roll_value")
            st.session_state.pop("perc_pct_field", None)
            st.session_state["perc_pct_field"] = _pv
        prow = st.columns([5, 1])
        with prow[0]:
            perc_s = st.text_input("Процент (0–100)", key="perc_pct_field")
        with prow[1]:
            st.markdown("<div style='height:1.85rem'></div>", unsafe_allow_html=True)
            if st.button("🎲", key="dice_perc", help="Случайный процент от 1 до 100"):
                st.session_state["_perc_roll_value"] = str(random.randint(1, 100))
                st.rerun()
        perc_desc = st.text_input("Процент — описание", key="perc_desc")
        if st.button("Добавить процент", key="add_perc"):
            pv = _parse_amount(perc_s, None)
            if pv is None:
                st.error("Введите число для процента.")
            else:
                pv = max(0, min(100, pv))
                st.session_state._rules.append({"type": "p", "val": pv, "desc": perc_desc or "пусто"})
                st.rerun()

    st.write("Порядок правил:")
    for i, r in enumerate(st.session_state._rules):
        if r.get("type") == "f":
            st.caption(f"{i+1}. Фикс: {r.get('val', 0)} — {r.get('desc', '')}")
        else:
            st.caption(f"{i+1}. Проц: {r.get('val', 0)}% — {r.get('desc', '')}")

    if st.button("Сохранить шаблон", key="save_tpl"):
        if not new_name.strip():
            st.error("Введите имя шаблона.")
        elif not st.session_state._rules:
            st.error("Добавьте хотя бы одно правило.")
        else:
            ok, err = dealer_input.save_template(username, new_name.strip(), list(st.session_state._rules))
            if ok:
                st.success(f"Шаблон «{new_name}» сохранён.")
                st.session_state._rules = []
                st.rerun()
            else:
                st.error(err or "Ошибка сохранения.")

with tab_piggy:
    st.subheader("Копилка")
    banks = get_piggybanks(username)
    if not banks:
        st.write("Копилок пока нет.")
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

    remains = st.session_state.get("fifo_remains")
    if remains is not None and remains > 0 and banks:
        st.write("Остаток после FIFO:")
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
    g_target_s = st.text_input("Целевая сумма", key="goal_target_str")
    g_link = st.text_input("Описание (необязательно)", key="goal_link")
    if st.button("Создать копилку", key="btn_create_goal"):
        g_target = _parse_float_amount(g_target_s, None)
        if g_name.strip() and g_target is not None and g_target > 0:
            bank = storage.PiggyBank(username)
            bank.create_goal(name=g_name.strip(), target=g_target, link=g_link or "")
            st.success(f"Копилка «{g_name}» создана.")
            st.rerun()
        else:
            st.error("Укажите название и целевую сумму.")

with tab_history:
    st.subheader("История расчётов (SQLite)")
    st.caption(f"База: `{user_records.db_path(username)}`")
    rows = user_records.fetch_recent(username, limit=30)
    if not rows:
        st.write("Записей пока нет — выполните расчёт FIFO.")
    else:
        for r in rows:
            with st.expander(f"{r['created_at']} · {r['template_name']} · ввод {r['input_amount']:.2f} → остаток {r['remainder']:.2f}"):
                if r.get("fail_rule_index") is not None:
                    st.warning(f"Не хватило с правила №{r['fail_rule_index']}")
                try:
                    lines = json.loads(r["history_json"] or "[]")
                    for line in lines:
                        st.text(line)
                except json.JSONDecodeError:
                    st.text(r.get("history_json", ""))

with tab_delete:
    st.subheader("Удалить шаблон")
    templates_all = get_templates(username)
    if not templates_all:
        st.caption("Нет шаблонов.")
    else:
        for name in templates_all:
            c1, c2 = st.columns([3, 1])
            with c1:
                st.write(f"📄 **{name}**")
            with c2:
                if st.button("Удалить", key=f"del_tpl_{name}"):
                    if delete_template(username, name):
                        st.success(f"Шаблон «{name}» удалён.")
                        st.rerun()
                    else:
                        st.error("Не удалось удалить.")

    st.divider()
    st.subheader("Удалить копилку")
    banks = get_piggybanks(username)
    bank_names = list(banks.keys())
    if not bank_names:
        st.caption("Нет копилок.")
    else:
        for name in bank_names:
            c1, c2 = st.columns([3, 1])
            with c1:
                d = banks[name]
                st.write(f"🐷 **{name}** — {d.get('current', 0):.0f} / {d.get('target', 0):.0f}")
            with c2:
                if st.button("Удалить", key=f"del_pig_{name}"):
                    if delete_piggybank(username, name):
                        st.success(f"Копилка «{name}» удалена.")
                        st.rerun()
                    else:
                        st.error("Не удалось удалить.")
import streamlit as st
from storage import StorageManager
import logic

# ── Theme palettes ────────────────────────────────────────────────────────────
DAY_THEME = {
    "bg":      "#F5F7FA",
    "sidebar": "#EAECF0",
    "card":    "#FFFFFF",
    "border":  "#D0D5DD",
    "text":    "#1A1A2E",
    "subtext": "#6C737A",
    "accent":  "#00A854",
    "danger":  "#E53935",
    "input":   "#FFFFFF",
}
NIGHT_THEME = {
    "bg":      "#0D1117",
    "sidebar": "#161B22",
    "card":    "#1C2128",
    "border":  "#30363D",
    "text":    "#E6EDF3",
    "subtext": "#8B949E",
    "accent":  "#00C853",
    "danger":  "#FF5252",
    "input":   "#21262D",
}

# ── Page config (must be first Streamlit call) ────────────────────────────────
st.set_page_config(page_title="FinLite 2.0", layout="wide", page_icon="💸")

# ── Session defaults ──────────────────────────────────────────────────────────
if "is_dark" not in st.session_state:
    st.session_state.is_dark = True

# ── Sidebar (toggle lives here — resolve theme AFTER this block) ──────────────
with st.sidebar:
    st.markdown("## 💸 FinLite Pro")
    # FIX: toggle is rendered first; theme is resolved below after the widget fires
    st.session_state.is_dark = st.toggle(
        "🌙 Ночной режим",
        value=st.session_state.is_dark,
    )
    st.divider()
    user = st.text_input("Логин", value="guest").lower()
    sm = StorageManager(user)

# ── Resolve theme AFTER toggle so it reflects the current rerun's state ───────
theme = NIGHT_THEME if st.session_state.is_dark else DAY_THEME

# ── CSS injection ─────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
/* ── Root & app shell ── */
html, body, .stApp, [data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section {{
    background-color: {theme['bg']} !important;
    color: {theme['text']} !important;
}}

/* ── Sidebar ── */
[data-testid="stSidebar"],
[data-testid="stSidebar"] > div {{
    background-color: {theme['sidebar']} !important;
    border-right: 1px solid {theme['border']} !important;
}}
[data-testid="stSidebar"] * {{
    color: {theme['text']} !important;
}}

/* ── Headings & generic text ── */
h1, h2, h3, h4, label, p, span, div {{
    color: {theme['text']} !important;
}}

/* ── Inputs ── */
.stTextInput input,
.stNumberInput input,
.stSelectbox > div > div,
.stTextArea textarea {{
    background-color: {theme['input']} !important;
    color: {theme['text']} !important;
    border: 1px solid {theme['border']} !important;
    border-radius: 6px !important;
}}
.stTextInput input:focus,
.stNumberInput input:focus {{
    border-color: {theme['accent']} !important;
    box-shadow: 0 0 0 2px {theme['accent']}33 !important;
}}

/* ── Buttons ── */
.stButton > button {{
    border: 1.5px solid {theme['accent']} !important;
    background: transparent !important;
    color: {theme['text']} !important;
    border-radius: 6px !important;
    transition: background 0.15s ease, color 0.15s ease;
}}
.stButton > button:hover {{
    background: {theme['accent']}22 !important;
    color: {theme['accent']} !important;
}}

/* ── Metrics ── */
[data-testid="stMetricValue"] {{
    color: {theme['accent']} !important;
    font-weight: 700 !important;
}}
[data-testid="stMetricLabel"] {{
    color: {theme['subtext']} !important;
}}

/* ── Expanders ── */
.stExpander {{
    background-color: {theme['card']} !important;
    border: 1px solid {theme['border']} !important;
    border-radius: 8px !important;
}}
.stExpander summary {{
    color: {theme['text']} !important;
}}

/* ── Tabs ── */
.stTabs [data-baseweb="tab-list"] {{
    background-color: transparent !important;
    border-bottom: 1px solid {theme['border']} !important;
    gap: 4px;
}}
.stTabs [data-baseweb="tab"] {{
    color: {theme['subtext']} !important;
    background: transparent !important;
    border-radius: 6px 6px 0 0 !important;
    padding: 8px 16px !important;
}}
.stTabs [aria-selected="true"] {{
    color: {theme['accent']} !important;
    border-bottom: 2px solid {theme['accent']} !important;
    background: {theme['accent']}11 !important;
}}

/* ── Table ── */
[data-testid="stTable"] table {{
    background-color: {theme['card']} !important;
    border: 1px solid {theme['border']} !important;
}}
[data-testid="stTable"] th {{
    background-color: {theme['sidebar']} !important;
    color: {theme['accent']} !important;
    border-bottom: 1px solid {theme['border']} !important;
}}
[data-testid="stTable"] td {{
    color: {theme['text']} !important;
    border-color: {theme['border']} !important;
}}

/* ── Download button ── */
.stDownloadButton > button {{
    border: 1.5px solid {theme['accent']} !important;
    background: {theme['accent']}18 !important;
    color: {theme['accent']} !important;
    border-radius: 6px !important;
}}

/* ── Divider ── */
hr {{
    border-color: {theme['border']} !important;
}}

/* ── Toggle ── */
[data-testid="stToggle"] span {{
    color: {theme['text']} !important;
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# TABS
# ─────────────────────────────────────────────────────────────────────────────
tabs = st.tabs(["💎 Расчет", "🛠 Шаблоны", "📜 История"])

# ── TAB 1: Calculation ────────────────────────────────────────────────────────
with tabs[0]:
    data = sm.load_user_data()

    if not data['templates']:
        st.info("Нет шаблонов. Создайте их во вкладке 🛠 Шаблоны.")
    else:
        col_in1, col_in2 = st.columns([2, 1])
        income = col_in1.number_input("Введите сумму дохода (₸)", min_value=0, step=5000)
        tpl_choice = col_in2.selectbox("Выберите шаблон", list(data['templates'].keys()))

        if st.button("🔥 Запустить FIFO расчет"):
            if income == 0:
                st.warning("Введите сумму дохода больше нуля.")
            else:
                res = logic.calculate_finance(income, data['templates'][tpl_choice], tpl_choice)

                c1, c2, c3 = st.columns(3)
                c1.metric("Остаток", f"{res['remainder']:,.0f} ₸")
                c2.metric("Удержано", f"{res['deducted']:,.0f} ₸", f"{res['percent']:.1f}%")

                # FIX: clamp progress to [0.0, 1.0] — avoids crash when deducted > income
                progress_val = max(0.0, min(1.0, 1.0 - (res['deducted'] / income)))
                c3.progress(progress_val)

                if res['fail_idx'] is not None:
                    st.error(f"⚠️ Баланс ушёл в минус на шаге {res['fail_idx']}!")

                with st.expander("📋 Детализация", expanded=True):
                    for line in res['history']:
                        st.write(line)

                sm.add_history({
                    "template": tpl_choice,
                    "input": income,
                    "remainder": res['remainder'],
                    "deducted": res['deducted'],
                })

# ── TAB 2: Template CRUD ──────────────────────────────────────────────────────
with tabs[1]:
    st.subheader("Управление шаблонами")
    data = sm.load_user_data()

    # Add new template
    with st.expander("➕ Новый шаблон"):
        new_name = st.text_input("Название шаблона", key="new_tpl_name")
        if st.button("Создать", key="create_tpl"):
            if new_name and new_name not in data['templates']:
                data['templates'][new_name] = []
                sm.save_user_data(data)
                st.success(f"Шаблон «{new_name}» создан.")
                st.rerun()
            elif not new_name:
                st.warning("Введите название.")
            else:
                st.warning("Шаблон с таким именем уже существует.")

    for t_name, rules in list(data['templates'].items()):
        with st.expander(f"⚙️ {t_name}"):
            col_dup, col_del = st.columns([1, 1])

            if col_dup.button("👯 Дублировать", key=f"dup_{t_name}"):
                data['templates'][f"{t_name}_copy"] = rules.copy()
                sm.save_user_data(data)
                st.rerun()

            if col_del.button("🗑 Удалить шаблон", key=f"del_{t_name}"):
                del data['templates'][t_name]
                sm.save_user_data(data)
                st.rerun()

            st.markdown("**Правила:**")
            updated_rules = []
            for i, r in enumerate(rules):
                c1, c2, c3 = st.columns([1, 2, 4])
                r_type = c1.selectbox(
                    "Тип", ["f", "p"],
                    index=0 if r['type'] == 'f' else 1,
                    key=f"type_{t_name}_{i}",
                )
                r_val = c2.number_input("Значение", value=float(r['val']), key=f"val_{t_name}_{i}")
                r_desc = c3.text_input("Описание", value=r['desc'], key=f"desc_{t_name}_{i}")
                updated_rules.append({"type": r_type, "val": r_val, "desc": r_desc})

            # Add rule button
            if st.button("➕ Добавить правило", key=f"add_rule_{t_name}"):
                data['templates'][t_name] = updated_rules + [{"type": "f", "val": 0, "desc": "Новое правило"}]
                sm.save_user_data(data)
                st.rerun()

            if st.button("✅ Сохранить изменения", key=f"save_{t_name}"):
                data['templates'][t_name] = updated_rules
                sm.save_user_data(data)
                st.success("Обновлено!")

# ── TAB 3: History ────────────────────────────────────────────────────────────
with tabs[2]:
    st.subheader("Лог операций")
    history = sm.get_history()

    if not history:
        st.info("История пуста. Запустите расчёт во вкладке 💎 Расчет.")
    else:
        st.download_button(
            "📥 Экспорт в CSV",
            data=sm.export_history_csv(),
            file_name="fin_history.csv",
            mime="text/csv",
        )
        st.table(history)

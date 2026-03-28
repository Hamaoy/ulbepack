import streamlit as st
import math
import os

# ================== CONFIG ==================
st.set_page_config(page_title="ULBE Production Pro+", layout="wide")

# ================== STYLE ==================
st.markdown("""
<style>
html, body, [class*="css"] {
    background-color: #FDFCF8 !important;
    color: #1A1A1A !important;
}
.result-card {
    background:#fff;
    padding:20px;
    border-radius:12px;
    border:2px solid #004E96;
    margin-top:15px
}
</style>
""", unsafe_allow_html=True)

# ================== LOGIN ==================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 Login")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if password == "ulbe2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("Wrong password")
    st.stop()

# ================== LOGO ==================
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if os.path.exists("logo.png"):
        st.image("logo.png")

# ================== LANGUAGE ==================
lang = st.radio("Language", ["AR", "TR"], horizontal=True)

TEXT = {
    "AR": {
        "title": "نظام ULBE",
        "box": "نوع العلبة",
        "print": "الطباعة",
        "qty": "الكمية",
        "calc": "احسب"
    },
    "TR": {
        "title": "ULBE Sistem",
        "box": "Kutu Tipi",
        "print": "Baskı",
        "qty": "Adet",
        "calc": "Hesapla"
    }
}[lang]

# ================== BOX TYPES ==================
BOX_TYPES = {
    "AR": {
        "علبة وقبغ": "kapak",
        "علبة مغناطيسية": "magnetic",
        "علبة شريط": "ribbon",
        "علبة جرارة": "drawer"
    },
    "TR": {
        "Kutu Kapak": "kapak",
        "Mıknatıslı Kutu": "magnetic",
        "Kurdele Kutu": "ribbon",
        "Çekmece Kutu": "drawer"
    }
}

# ================== SIDEBAR ==================
with st.sidebar:
    default_prices = {
        "p_b": 1200,
        "p_p": 250,
        "dig": 400,
        "rib": 0,
        "mag": 0,
        "lab": 5000,
        "mold": 100000,
        "print": 40000,
        "lam": 60000,
        "cut": 130000,
        "zinc": 10000
    }

    if 'p' not in st.session_state:
        st.session_state.p = default_prices.copy()

    ps = st.session_state.p

    if st.button("Reset"):
        st.session_state.p = default_prices.copy()
        st.rerun()

    st.subheader("Materials")
    ps["p_b"] = st.number_input("Board", value=ps["p_b"])
    ps["p_p"] = st.number_input("Offset Paper", value=ps["p_p"])
    ps["dig"] = st.number_input("Digital Paper", value=ps["dig"])

    st.subheader("Extras")
    ps["rib"] = st.number_input("Ribbon / piece", value=ps["rib"])
    ps["mag"] = st.number_input("Magnet / piece", value=ps["mag"])

    st.subheader("Work")
    ps["lab"] = st.number_input("Labor / piece", value=ps["lab"])
    ps["mold"] = st.number_input("Mold", value=ps["mold"])
    ps["print"] = st.number_input("Printing", value=ps["print"])
    ps["lam"] = st.number_input("Lamination", value=ps["lam"])
    ps["cut"] = st.number_input("Cutting", value=ps["cut"])
    ps["zinc"] = st.number_input("Plate per color", value=ps["zinc"])

    waste_ratio = st.number_input("Waste %", value=10) / 100

# ================== INPUT ==================
st.title(TEXT["title"])

col1, col2 = st.columns(2)

with col1:
    box_type = st.selectbox(TEXT["box"], list(BOX_TYPES[lang].keys()))
    print_method = st.radio(TEXT["print"], ["Offset", "Digital"])
    colors = st.number_input("Colors", value=4)
    qty = st.number_input(TEXT["qty"], value=1000)

with col2:
    L = st.number_input("L", value=20.0)
    W = st.number_input("W", value=15.0)
    H = st.number_input("H", value=5.0)

# ================== CORE FUNCTIONS ==================
def get_parts(L, W, H, box_key):
    if box_key == "kapak":
        return [("Base", L+2*H, W+2*H), ("Lid", L+6.5, W+6.5)]
    else:
        return [("Main", L+2*H, W+2*H)]

def fit(sw, sh, w, h):
    if w > sw or h > sh:
        return 0
    return max((sw//w)*(sh//h), (sh//w)*(sw//h))

def calc_part(sw, sh, name, w, h, qty):
    per_sheet = fit(sw, sh, w, h)
    sheets = math.ceil(qty / per_sheet) if per_sheet else 0
    return {
        "name": name,
        "per_sheet": per_sheet,
        "sheets": sheets
    }

# ================== CALC ==================
if st.button(TEXT["calc"]):

    box_key = BOX_TYPES[lang][box_type]
    parts = get_parts(L, W, H, box_key)

    sw, sh = (70, 100) if print_method == "Offset" else (33, 70)

    details = []
    total_board = 0

    for name, w, h in parts:
        d = calc_part(sw, sh, name, w, h, qty)
        details.append(d)
        total_board += d["sheets"]

    # Waste
    total_board = math.ceil(total_board * (1 + waste_ratio))
    total_paper = total_board

    # Costs
    cost_board = total_board * ps['p_b']
    paper_price = ps['p_p'] if print_method == "Offset" else ps['dig']
    cost_paper = total_paper * paper_price
    zinc_cost = colors * ps['zinc'] if print_method == "Offset" else 0

    ribbon_cost = ps['rib'] * qty
    magnet_cost = ps['mag'] * qty
    labor_cost = ps['lab'] * qty

    if print_method == "Digital":
        total = cost_board + cost_paper + ribbon_cost + magnet_cost
    else:
        total = (cost_board + cost_paper + zinc_cost +
                 ribbon_cost + magnet_cost + labor_cost +
                 ps['mold'] + ps['print'] + ps['lam'] + ps['cut'])

    # ================== OUTPUT ==================
    st.markdown("### 📦 Sheet Details")

    for d in details:
        st.write(f"{d['name']} Board: {d['per_sheet']} per sheet → {d['sheets']} sheets")

    st.markdown(f"""
    <div class='result-card'>

    <h3>Production Cost Breakdown</h3>

    Board Cost: {cost_board:,.0f}<br>
    Paper Cost: {cost_paper:,.0f}<br>
    Zinc Plates: {zinc_cost:,.0f}<br>
    Ribbon: {ribbon_cost:,.0f}<br>
    Magnet: {magnet_cost:,.0f}<br>
    Labor: {labor_cost:,.0f}<br>
    Mold: {ps['mold']:,.0f}<br>
    Printing: {ps['print']:,.0f}<br>
    Lamination: {ps['lam']:,.0f}<br>
    Cutting: {ps['cut']:,.0f}<br>

    <hr>

    <h2>Total: {total:,.0f}</h2>
    <h3>Unit Price: {total/qty:,.0f}</h3>

    </div>
    """, unsafe_allow_html=True)

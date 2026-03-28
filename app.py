import streamlit as st
import math
import os

st.set_page_config(page_title="ULBE Production Pro+", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
html, body {
    background:#FDFCF8 !important;
    color:#1A1A1A !important;
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

# ================= LOGIN =================
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

# ================= LOGO =================
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if os.path.exists("logo.png"):
        st.image("logo.png")

# ================= LANGUAGE =================
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

# ================= BOX TYPES =================
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

# ================= SIDEBAR =================
with st.sidebar:

    default_prices = {
        "board": 1200,
        "offset": 250,
        "digital": 400,
        "labor": 5000,
        "zinc": 10000,
        "mold": 100000,
        "print": 40000,
        "lam": 60000,
        "cut": 130000,
        "waste": 0.02
    }

    if "p" not in st.session_state:
        st.session_state.p = default_prices.copy()

    ps = st.session_state.p

    if st.button("Reset"):
        st.session_state.p = default_prices.copy()
        st.rerun()

    st.subheader("Materials")
    ps["board"] = st.number_input("Board", value=ps["board"])
    ps["offset"] = st.number_input("Offset Paper", value=ps["offset"])
    ps["digital"] = st.number_input("Digital Paper", value=ps["digital"])

    st.subheader("Work")
    ps["labor"] = st.number_input("Labor / piece", value=ps["labor"])
    ps["zinc"] = st.number_input("Plate / color", value=ps["zinc"])
    ps["mold"] = st.number_input("Mold", value=ps["mold"])
    ps["print"] = st.number_input("Printing", value=ps["print"])
    ps["lam"] = st.number_input("Lamination", value=ps["lam"])
    ps["cut"] = st.number_input("Cutting", value=ps["cut"])

    ps["waste"] = st.number_input("Waste %", value=int(ps["waste"]*100)) / 100

# ================= INPUT =================
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

# ================= CORE =================
def get_parts(L, W, H, key):
    if key == "kapak":
        return [("Base", L+2*H, W+2*H), ("Lid", L+6.5, W+6.5)]
    else:
        return [("Main", L+2*H, W+2*H)]

def fit(sw, sh, w, h):
    if w > sw or h > sh:
        return 0
    return max((sw//w)*(sh//h), (sh//w)*(sw//h))

def calc_details(parts, sw, sh):
    details = []
    total = 0
    for name, w, h in parts:
        per = fit(sw, sh, w, h)
        sheets = math.ceil(qty / per) if per else 0
        details.append((name, per, sheets))
        total += sheets
    return details, total

def smart_combine(parts):
    if len(parts) != 2:
        return None

    (_, w1, h1), (_, w2, h2) = parts

    sep = sum([math.ceil(qty / fit(70,100,w,h)) for _,w,h in parts])

    comb_h = math.ceil(qty / fit(70,100, w1+w2, max(h1,h2)))
    comb_v = math.ceil(qty / fit(70,100, max(w1,w2), h1+h2))

    return min(sep, comb_h, comb_v)

# ================= CALC =================
if st.button(TEXT["calc"]):

    box_key = BOX_TYPES[lang][box_type]
    parts = get_parts(L, W, H, box_key)

    # ===== BOARD =====
    board_details, board_total = calc_details(parts, 70, 100)

    # Smart combine
    combined = smart_combine(parts)
    if combined:
        board_total = combined

    # ===== PAPER =====
    if print_method == "Offset":
        pw, ph = 70, 100
    else:
        pw, ph = 33, 70

    paper_details, paper_total = calc_details(parts, pw, ph)

    # ===== WASTE =====
    board_total = math.ceil(board_total * (1 + ps["waste"]))
    paper_total = math.ceil(paper_total * (1 + ps["waste"]))

    # ===== COST =====
    cost_board = board_total * ps["board"]
    paper_price = ps["offset"] if print_method == "Offset" else ps["digital"]
    cost_paper = paper_total * paper_price
    labor = ps["labor"] * qty
    zinc = colors * ps["zinc"] if print_method == "Offset" else 0

    total = (cost_board + cost_paper + labor +
             zinc + ps["mold"] + ps["print"] + ps["lam"] + ps["cut"])

    # ================= OUTPUT =================
    st.markdown("### Board Details")
    for n, per, s in board_details:
        st.write(f"{n} Board: {per} per sheet → {s} sheets")

    st.markdown("### Paper Details")
    for n, per, s in paper_details:
        st.write(f"{n} Paper: {per} per sheet → {s} sheets")

    st.markdown(f"""
    <div class='result-card'>

    <h3>Production Cost Breakdown</h3>

    Board Cost: {cost_board:,.0f}<br>
    Paper Cost: {cost_paper:,.0f}<br>
    Labor: {labor:,.0f}<br>
    Zinc Plates: {zinc:,.0f}<br>
    Mold: {ps["mold"]:,.0f}<br>
    Printing: {ps["print"]:,.0f}<br>
    Lamination: {ps["lam"]:,.0f}<br>
    Cutting: {ps["cut"]:,.0f}<br>

    <hr>

    <h2>Total: {total:,.0f}</h2>
    <h3>Unit Price: {total/qty:,.0f}</h3>

    </div>
    """, unsafe_allow_html=True)

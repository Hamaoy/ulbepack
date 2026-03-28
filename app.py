import streamlit as st
import math
import os

st.set_page_config(page_title="ULBE Production Pro+", layout="wide")

# ================== STYLE (FIX DARK MODE) ==================
st.markdown("""
<style>
html, body, [class*="css"]  {
    background-color: #FDFCF8 !important;
    color: #1A1A1A !important;
}
.result-card { background:#fff;padding:20px;border-radius:12px;border:2px solid #004E96;margin-top:15px }
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

T = {
    "AR": {
        "title":"نظام ULBE",
        "box":"نوع العلبة",
        "print":"الطباعة",
        "qty":"الكمية",
        "calc":"احسب",
        "total":"الإجمالي",
        "unit":"سعر القطعة"
    },
    "TR": {
        "title":"ULBE Sistem",
        "box":"Kutu Tipi",
        "print":"Baskı",
        "qty":"Adet",
        "calc":"Hesapla",
        "total":"Toplam",
        "unit":"Birim"
    }
}[lang]

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
        "zinc": 25000
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
    ps["rib"] = st.number_input("Ribbon cost per piece", value=ps["rib"])
    ps["mag"] = st.number_input("Magnet cost per piece", value=ps["mag"])

    st.subheader("Work")
    ps["lab"] = st.number_input("Labor per piece", value=ps["lab"])
    ps["mold"] = st.number_input("Printing Plates", value=ps["mold"])
    ps["print"] = st.number_input("Printing", value=ps["print"])
    ps["lam"] = st.number_input("Lamination", value=ps["lam"])
    ps["cut"] = st.number_input("Cutting", value=ps["cut"])
    ps["zinc"] = st.number_input("Plate per color", value=ps["zinc"])

# ================== INPUT ==================
st.title(T["title"])

col1, col2 = st.columns(2)

with col1:
    box_type = st.selectbox(T["box"], [
        "Kutu Kapak",
        "Mıknatıslı Kutu",
        "Kurdele Kutu",
        "Çekmece Kutu"
    ])

    print_method = st.radio(T["print"], ["Offset", "Digital"])
    colors = st.number_input("Colors", value=4)
    qty = st.number_input(T["qty"], value=1000)

with col2:
    L = st.number_input("L", value=20.0)
    W = st.number_input("W", value=15.0)
    H = st.number_input("H", value=5.0)

# ================== STRUCTURE ==================
def get_parts(L,W,H,t):
    if "Kutu Kapak" in t:
        return [(L+2*H,W+2*H),(L+6.5,W+6.5)]
    else:
        return [(L+2*H,W+2*H)]

# ================== FIT ==================
def fit(sw,sh,w,h):
    if w>sw or h>sh: return 0
    return max((sw//w)*(sh//h),(sh//w)*(sw//h))

# ================== CALC ==================
if st.button(T["calc"]):

    parts = get_parts(L,W,H,box_type)

    sw,sh = (70,100) if print_method=="Offset" else (33,70)

    total_board = 0

    # دمج ذكي بسيط
    if len(parts)==2:
        w1,h1 = parts[0]
        w2,h2 = parts[1]

        sep = math.ceil(qty/fit(70,100,w1,h1)) + math.ceil(qty/fit(70,100,w2,h2))
        comb = math.ceil(qty/fit(70,100,w1+w2,max(h1,h2)))

        total_board = min(sep,comb)
    else:
        w,h = parts[0]
        total_board = math.ceil(qty/fit(70,100,w,h))

    total_paper = total_board

    cost_board = total_board * ps['p_b']
    paper_price = ps['p_p'] if print_method=="Offset" else ps['dig']
    cost_paper = total_paper * paper_price

    zinc_cost = colors * ps['zinc'] if print_method=="Offset" else 0

    ribbon_cost = ps['rib'] * qty
    magnet_cost = ps['mag'] * qty

    labor_cost = ps['lab'] * qty

    if print_method == "Digital":
        total = cost_board + cost_paper + ribbon_cost + magnet_cost
    else:
        total = cost_board + cost_paper + zinc_cost + ribbon_cost + magnet_cost + labor_cost + ps['mold'] + ps['print'] + ps['lam'] + ps['cut']

    st.markdown(f"""
    <div class='result-card'>

    الكارتون: {total_board} × {ps['p_b']} = {cost_board:,.0f}<br>
    الورق: {total_paper} × {paper_price} = {cost_paper:,.0f}<br>

    قوالب الطبع: {zinc_cost:,.0f}<br>
    الشريط: {ribbon_cost:,.0f}<br>
    المغناطيس: {magnet_cost:,.0f}<br>

    العمال: {ps['lab']} × {qty} = {labor_cost:,.0f}<br>
    القالب: {ps['mold']:,.0f}<br>
    الطبع: {ps['print']:,.0f}<br>
    السلفنة: {ps['lam']:,.0f}<br>
    تقطيع الكرتون والورق: {ps['cut']:,.0f}<br>

    <hr>
    <h2>{T['total']}: {total:,.0f}</h2>
    <h3>{T['unit']}: {total/qty:,.0f}</h3>
    </div>
    """, unsafe_allow_html=True)

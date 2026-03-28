import streamlit as st
import math
import os

st.set_page_config(page_title="ULBE Production Pro+", layout="wide")

# ================== LOGIN ==================
if "auth" not in st.session_state:
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("🔐 تسجيل الدخول | Login")
    password = st.text_input("كلمة المرور / Password", type="password")
    if st.button("دخول / Login"):
        if password == "ulbe2026":
            st.session_state.auth = True
            st.rerun()
        else:
            st.error("كلمة المرور غير صحيحة")
    st.stop()

# ================== STYLE ==================
st.markdown("""
<style>
.stApp { background-color: #FDFCF8; color: #1A1A1A; }
.result-card { background:#fff;padding:20px;border-radius:12px;border:2px solid #004E96;margin-top:15px }
</style>
""", unsafe_allow_html=True)

# ================== LOGO ==================
col1, col2, col3 = st.columns([1,2,1])
with col2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)

# ================== LANGUAGE ==================
lang = st.radio("🌐 Language / اللغة", ["AR", "TR"], horizontal=True)

# ================== TEXT ==================
T = {
    "AR": {
        "title":"نظام ULBE الذكي",
        "box":"نوع العلبة",
        "print":"الطباعة",
        "qty":"الكمية",
        "calc":"احسب",
        "total":"الإجمالي",
        "unit":"سعر القطعة"
    },
    "TR": {
        "title":"ULBE Akıllı Sistem",
        "box":"Kutu Tipi",
        "print":"Baskı",
        "qty":"Adet",
        "calc":"Hesapla",
        "total":"Toplam",
        "unit":"Birim Fiyat"
    }
}[lang]

# ================== DEFAULT PRICES ==================
with st.sidebar:
    st.header("💰 التحكم بالاسعار / Fiyatlar")

    default_prices = {
        "p_b": 1200,
        "p_p": 250,
        "dig": 400,      # 🔥 ديجيتال 400
        "rib": 300,
        "lab": 5000,     # 🔥 عامل للوحدة
        "mold": 100000,
        "print": 40000,
        "lam": 60000,
        "cut": 130000,
        "zinc": 25000,
        "waste": 5
    }

    if 'p' not in st.session_state:
        st.session_state.p = default_prices.copy()

    ps = st.session_state.p

    if st.button("🔄 Reset"):
        st.session_state.p = default_prices.copy()
        st.rerun()

    ps["p_b"] = st.number_input("سعر الكارتون", value=ps["p_b"])
    ps["p_p"] = st.number_input("سعر ورق اوفست", value=ps["p_p"])
    ps["dig"] = st.number_input("سعر ورق ديجيتال", value=ps["dig"])
    ps["rib"] = st.number_input("سعر متر الشريط", value=ps["rib"])

    st.markdown("---")
    ps["lab"] = st.number_input("اجور العامل (للقطعة)", value=ps["lab"])
    ps["mold"] = st.number_input("القالب", value=ps["mold"])
    ps["print"] = st.number_input("الطبع", value=ps["print"])
    ps["lam"] = st.number_input("السلفنة", value=ps["lam"])
    ps["cut"] = st.number_input("الداي كت", value=ps["cut"])
    ps["zinc"] = st.number_input("سعر الزنك/لون", value=ps["zinc"])
    ps["waste"] = st.number_input("نسبة الهدر %", value=ps["waste"])

# ================== INPUTS ==================
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
def get_parts(L, W, H, t):
    parts = []

    if "Kutu Kapak" in t:
        parts += [
            ("Base Board", L+2*H, W+2*H, 'b'),
            ("Lid Board", L+6.5, W+6.5, 'b'),
            ("Base Paper", L+2*H+4.5, W+2*H+4.5, 'p'),
            ("Lid Paper", L+11, W+11, 'p')
        ]

    elif "Çekmece" in t:
        parts += [
            ("Drawer", L+2*H, W+2*H, 'b'),
            ("Sleeve", 2*W+2*H+2, L, 'b'),
            ("Drawer Paper", L+2*H+4.5, W+2*H+4.5, 'p'),
            ("Sleeve Paper", 2*W+2*H+7, L+4.5, 'p'),
            ("Inner", 2*L+2*H, W, 'p')
        ]

    else:
        parts += [
            ("Base", L+2*H, W+2*H, 'b'),
            ("Cover", 2*L+2*H+2, W+1, 'b'),
            ("Base Paper", L+2*H+4.5, W+2*H+4.5, 'p'),
            ("Cover Paper", 2*L+2*H+7, W+5, 'p'),
            ("Inner", 2*L+2*H, W, 'p')
        ]

    return parts

# ================== NESTING ==================
def fit(sheet_w, sheet_h, w, h):
    if w > sheet_w or h > sheet_h:
        return 0
    return max((sheet_w//w)*(sheet_h//h), (sheet_h//w)*(sheet_w//h))

# 🔥 Smart Combine (قطعتين)
def combine_fit(w1,h1,w2,h2,sw,sh):
    side = fit(sw,sh,w1+w2,max(h1,h2))
    top = fit(sw,sh,max(w1,w2),h1+h2)
    return max(side,top)

# ================== CALC ==================
if st.button(T["calc"]):

    parts = get_parts(L, W, H, box_type)

    sheet_w, sheet_h = (70,100) if print_method=="Offset" else (33,70)

    board_parts = [p for p in parts if p[3]=='b']
    paper_parts = [p for p in parts if p[3]=='p']

    total_board = 0
    total_paper = 0

    # 🔥 كارتون دمج
    if len(board_parts) >= 2:
        (n1,w1,h1,_),(n2,w2,h2,_) = board_parts[:2]
        sep = math.ceil(qty/fit(70,100,w1,h1)) + math.ceil(qty/fit(70,100,w2,h2))
        comb = math.ceil(qty/combine_fit(w1,h1,w2,h2,70,100))
        total_board = min(sep,comb)
    else:
        for _,w,h,_ in board_parts:
            total_board += math.ceil(qty/fit(70,100,w,h))

    # 🔥 ورق دمج
    if len(paper_parts) >= 2:
        (n1,w1,h1,_),(n2,w2,h2,_) = paper_parts[:2]
        sep = math.ceil(qty/fit(sheet_w,sheet_h,w1,h1)) + math.ceil(qty/fit(sheet_w,sheet_h,w2,h2))
        comb = math.ceil(qty/combine_fit(w1,h1,w2,h2,sheet_w,sheet_h))
        total_paper = min(sep,comb)
    else:
        for _,w,h,_ in paper_parts:
            total_paper += math.ceil(qty/fit(sheet_w,sheet_h,w,h))

    # ================= COST =================
    cost_board = total_board * ps['p_b']
    paper_price = ps['p_p'] if print_method=="Offset" else ps['dig']
    cost_paper = total_paper * paper_price

    zinc_cost = colors * ps['zinc'] if print_method=="Offset" else 0
    ribbon_cost = qty * 0.6 * ps['rib'] if "Kurdele" in box_type else 0

    labor_cost = ps['lab'] * qty

    if print_method == "Digital":
        total = cost_board + cost_paper + ribbon_cost
    else:
        total = cost_board + cost_paper + zinc_cost + ribbon_cost + labor_cost + ps['mold'] + ps['print'] + ps['lam'] + ps['cut']

    st.markdown(f"""
    <div class='result-card'>

    <b>تفاصيل الكارتون:</b><br>
    {total_board} × {ps['p_b']} = {cost_board:,.0f}<br><br>

    <b>تفاصيل الورق:</b><br>
    {total_paper} × {paper_price} = {cost_paper:,.0f}<br><br>

    <b>الزنك:</b> {zinc_cost:,.0f}<br>
    <b>الشريط:</b> {ribbon_cost:,.0f}<br><br>

    <b>اجور العمل:</b><br>
    {ps['lab']} × {qty} = {labor_cost:,.0f}<br>
    قالب: {ps['mold']:,.0f}<br>
    طبع: {ps['print']:,.0f}<br>
    سلفنة: {ps['lam']:,.0f}<br>
    دايكت: {ps['cut']:,.0f}<br>

    <hr>
    <h2>{T['total']}: {total:,.0f}</h2>
    <h3>{T['unit']}: {total/qty:,.0f}</h3>
    </div>
    """, unsafe_allow_html=True)

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
# 🟢 قائمة الأسعار + زر Reset
with st.sidebar:
    st.header("💰 التحكم بالاسعار")

    default_prices = {
        "p_b": 1200,
        "p_p": 250,
        "dig": 1500,
        "rib": 300,
        "lab": 50000,
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

    if st.button("🔄 Reset الأسعار"):
        st.session_state.p = default_prices.copy()
        st.rerun()

    ps["p_b"] = st.number_input("سعر الكارتون", value=ps["p_b"])
    ps["p_p"] = st.number_input("سعر ورق اوفست", value=ps["p_p"])
    ps["dig"] = st.number_input("سعر ورق ديجيتال", value=ps["dig"])
    ps["rib"] = st.number_input("سعر متر الشريط", value=ps["rib"])

    st.markdown("---")
    ps["lab"] = st.number_input("اجور العمال", value=ps["lab"])
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
        "علبة وقبغ (قطعتين)",
        "علبة مغناطيسية",
        "علبة شريط (Kurdele)",
        "علبة جرارة (مجر)"
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

    if "وقبغ" in t:
        parts += [
            ("Base Board", L+2*H, W+2*H, 'b'),
            ("Lid Board", L+6.5, W+6.5, 'b'),
            ("Base Paper", L+2*H+4.5, W+2*H+4.5, 'p'),
            ("Lid Paper", L+11, W+11, 'p')
        ]

    elif "جرارة" in t:
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

# ================== CALC ==================
if st.button(T["calc"]):

    parts = get_parts(L, W, H, box_type)

    sheet_w, sheet_h = (70,100) if print_method=="Offset" else (33,70)

    total_board = 0
    total_paper = 0

    # نحسب كلشي بالبداية حتى نتجنب الاخطاء
    cost_board = 0
    cost_paper = 0
    zinc_cost = 0
    ribbon_cost = 0

    for name,w,h,t in parts:
        sw,sh = (70,100) if t=='b' else (sheet_w,sheet_h)

        per = fit(sw,sh,w,h)

        if per == 0:
            st.error(f"❌ {name} too big")
            continue

        sheets = math.ceil(qty/per)
        sheets *= (1 + ps['waste']/100)

        if t=='b': 
            total_board += sheets
        else: 
            total_paper += sheets

        st.write(f"{name}: {int(per)} per sheet → {int(sheets)} sheets")

    # نحسب التكاليف بعد اللوب
    cost_board = total_board * ps['p_b']
    paper_price = ps['p_p'] if print_method=="Offset" else ps['dig']
    cost_paper = total_paper * paper_price

    zinc_cost = colors * ps['zinc'] if print_method=="Offset" else 0
    ribbon_cost = qty * 0.6 * ps['rib'] if "Kurdele" in box_type else 0

    # منطق الطباعة
    if print_method == "Digital":
        total = cost_board + cost_paper + ribbon_cost
    else:
        total = cost_board + cost_paper + zinc_cost + ribbon_cost + ps['lab'] + ps['mold'] + ps['print'] + ps['lam'] + ps['cut']

    st.markdown(f"""
    <div class='result-card'>

    <b>تفاصيل الكارتون:</b><br>
    {int(total_board)} × {ps['p_b']} = {int(cost_board)}<br><br>

    <b>تفاصيل الورق:</b><br>
    {int(total_paper)} × {paper_price} = {int(cost_paper)}<br><br>

    <b>الزنك:</b> {int(zinc_cost)}<br>
    <b>الشريط:</b> {int(ribbon_cost)}<br><br>

    <b>اجور العمل:</b><br>
    عمال: {ps['lab']}<br>
    قالب: {ps['mold']}<br>
    طبع: {ps['print']}<br>
    سلفنة: {ps['lam']}<br>
    دايكت: {ps['cut']}<br>

    <hr>
    <h2>{T['total']}: {int(total)}</h2>
    <h3>{T['unit']}: {int(total/qty)}</h3>
    </div>
    """, unsafe_allow_html=True)

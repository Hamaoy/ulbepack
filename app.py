import streamlit as st
import math

st.set_page_config(page_title="ULBE Production Pro+", layout="wide")

# ================== STYLE ==================
st.markdown("""
<style>
.stApp { background-color: #FDFCF8; color: #1A1A1A; }
.result-card { background:#fff;padding:20px;border-radius:12px;border:2px solid #004E96;margin-top:15px }
</style>
""", unsafe_allow_html=True)

# ================== DEFAULT PRICES ==================
if 'p' not in st.session_state:
    st.session_state.p = {
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

ps = st.session_state.p

# ================== INPUTS ==================
st.title("ULBE Smart Calculator PRO 🚀")

col1, col2 = st.columns(2)

with col1:
    box_type = st.selectbox("نوع العلبة", [
        "علبة وقبغ (قطعتين)",
        "علبة مغناطيسية",
        "علبة شريط (Kurdele)",
        "علبة جرارة (مجر)"
    ])

    print_method = st.radio("الطباعة", ["Offset", "Digital"])
    colors = st.number_input("عدد الألوان (Offset فقط)", value=4)
    qty = st.number_input("الكمية", value=1000)

with col2:
    L = st.number_input("L", value=20.0)
    W = st.number_input("W", value=15.0)
    H = st.number_input("H", value=5.0)

# ================== STRUCTURE ==================
def get_parts(L, W, H, t):
    parts = []

    if t == "علبة وقبغ (قطعتين)":
        parts += [
            ("كارتون الحوض", L+2*H, W+2*H, 'b'),
            ("كارتون القبغ", L+6.5, W+6.5, 'b'),
            ("ورق الحوض", L+2*H+4.5, W+2*H+4.5, 'p'),
            ("ورق القبغ", L+11, W+11, 'p')
        ]

    elif t == "علبة جرارة (مجر)":
        parts += [
            ("كارتون المجر", L+2*H, W+2*H, 'b'),
            ("كارتون الكفر", 2*W+2*H+2, L, 'b'),
            ("ورق المجر", L+2*H+4.5, W+2*H+4.5, 'p'),
            ("ورق الكفر", 2*W+2*H+7, L+4.5, 'p'),
            ("بطانة داخلية", 2*L+2*H, W, 'p')
        ]

    elif t in ["علبة مغناطيسية", "علبة شريط (Kurdele)"]:
        parts += [
            ("كارتون الحوض", L+2*H, W+2*H, 'b'),
            ("كارتون الغلاف", 2*L+2*H+2, W+1, 'b'),
            ("ورق الحوض", L+2*H+4.5, W+2*H+4.5, 'p'),
            ("ورق الغلاف", 2*L+2*H+7, W+5, 'p'),
            ("بطانة داخلية", 2*L+2*H, W, 'p')
        ]

    return parts

# ================== NESTING ==================
def fit(sheet_w, sheet_h, w, h):
    if w > sheet_w or h > sheet_h:
        return 0
    return max((sheet_w//w)*(sheet_h//h), (sheet_h//w)*(sheet_w//h))

# ================== CALC ==================
if st.button("احسب"):

    parts = get_parts(L, W, H, box_type)

    sheet_w, sheet_h = (70,100) if print_method=="Offset" else (33,70)

    total_board = 0
    total_paper = 0

    st.subheader("تفاصيل الإنتاج")

    for name,w,h,t in parts:
        sw,sh = (70,100) if t=='b' else (sheet_w,sheet_h)

        per = fit(sw,sh,w,h)

        if per == 0:
            st.error(f"❌ {name} لا يمكن طباعته على الشيت")
            continue

        sheets = math.ceil(qty/per)
        sheets *= (1 + ps['waste']/100)

        if t=='b': total_board += sheets
        else: total_paper += sheets

        st.write(f"{name}: {int(per)} باللوح → تحتاج {int(sheets)} لوح")

    # ================= COST =================
    cost_board = total_board * ps['p_b']
    paper_price = ps['p_p'] if print_method=="Offset" else ps['dig']
    cost_paper = total_paper * paper_price

    zinc_cost = colors * ps['zinc'] if print_method=="Offset" else 0
    ribbon_cost = qty * 0.6 * ps['rib'] if box_type=="علبة شريط (Kurdele)" else 0

    total = cost_board + cost_paper + zinc_cost + ribbon_cost + ps['lab'] + ps['mold'] + ps['print'] + ps['lam'] + ps['cut']

    st.markdown(f"""
    <div class='result-card'>
    الكارتون: {int(total_board)} × {ps['p_b']} = {int(cost_board)}<br>
    الورق: {int(total_paper)} × {paper_price} = {int(cost_paper)}<br>
    الزنك: {int(zinc_cost)}<br>
    الشريط: {int(ribbon_cost)}<br>
    <hr>
    <h2>الإجمالي: {int(total)}</h2>
    <h3>سعر القطعة: {int(total/qty)}</h3>
    </div>
    """, unsafe_allow_html=True)

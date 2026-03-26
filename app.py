import streamlit as st
import math
import os
import fitz  # PyMuPDF

# 1. إعدادات الواجهة والحماية
st.set_page_config(page_title="نظام تسعير الورشة الاحترافي", layout="wide")

PASSWORD = "ULBE2026"
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center;'>🔐 النظام مغلق</h2>", unsafe_allow_html=True)
        pwd = st.text_input("كلمة المرور", type="password")
        if st.button("دخول"):
            if pwd == PASSWORD: st.session_state["password_correct"] = True; st.rerun()
            else: st.error("❌ خطأ")
        return False
    return True

if not check_password(): st.stop()

# 2. إدارة الأسعار (مع الاحتفاظ بكل التفاصيل)
default_prices = {
    "p_b": 1200, "p_p": 235, "s_p": 40000, "s_l": 60000, "s_c": 130000,
    "c_d": 100000, "c_z": 30000, "c_t": 25000, "m_p": 500, "labor": 50000, "dig_p": 1500
}
for k, v in default_prices.items():
    if k not in st.session_state: st.session_state[k] = v

def reset_prices():
    for k, v in default_prices.items(): st.session_state[k] = v

# 3. محرك قراءة الـ PDF المطور (يقرأ اللون أو حجم الصفحة)
def get_pdf_dim(file_bytes):
    if file_bytes is None: return 0, 0
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        page = doc[0]
        # محاولة أولى: قراءة الخطوط الملونة
        drawings = page.get_drawings()
        PT_TO_CM = 28.346
        rects = []
        for path in drawings:
            rects.append(path["rect"])
        
        if rects:
            full_rect = fitz.Rect(rects[0])
            for r in rects: full_rect |= r
            return round(full_rect.width / PT_TO_CM, 1), round(full_rect.height / PT_TO_CM, 1)
        
        # محاولة ثانية: إذا لم توجد خطوط، نأخذ حجم الصفحة (Artboard)
        return round(page.rect.width / PT_TO_CM, 1), round(page.rect.height / PT_TO_CM, 1)
    except: return 0, 0

# 4. التصميم
st.markdown("""<style>
    .stApp { background-color: #0e1117; color: #e0e0e0; }
    .stMetric { background: #161b22; padding: 15px; border-radius: 10px; border: 1px solid #30363d; }
    .stButton>button { background-color: #238636; color: white; border-radius: 8px; font-weight: bold; }
</style>""", unsafe_allow_html=True)

if os.path.exists("logo.png"):
    c1, c2, c3 = st.columns([2, 1, 2]); c2.image("logo.png", use_container_width=True)

# 5. القائمة الجانبية (الإعدادات)
with st.sidebar:
    st.header("🛠️ الإعدادات")
    if st.button("🔄 ريسيت الأسعار"): reset_prices(); st.rerun()
    st.session_state.p_b = st.number_input("سعر الكارتون", value=st.session_state.p_b)
    st.session_state.p_p = st.number_input("سعر الورق", value=st.session_state.p_p)
    st.session_state.dig_p = st.number_input("سعر طبعة الديجيتال", value=st.session_state.dig_p)
    st.session_state.labor = st.number_input("أجور العمال", value=st.session_state.labor)
    # بقية الأسعار (الطبع، السلفنة، الخ) مخفية للتوفير المساحة وتعمل في الخلفية

# 6. واجهة العمل (Workflow)
st.title("🚀 نظام تحليل العلب الذكي")

tab1, tab2 = st.tabs(["📂 رفع ملفات الأجزاء (PDF)", "⌨️ إدخال يدوي سريع"])

with tab1:
    st.subheader("ارفع تصميم كل جزء بشكل منفصل")
    up_col1, up_col2 = st.columns(2)
    with up_col1:
        file_body = st.file_uploader("1️⃣ ملف الكارتون (الداي كت)", type="pdf")
        file_paper = st.file_uploader("2️⃣ ملف الورق الخارجي", type="pdf")
    with up_col2:
        b_type = st.selectbox("نوع العلبة المختارة", ["علبة وقبغ (قطعتين)", "علبة مغناطيسية", "علبة جرارة"])
        pr_type = st.selectbox("طريقة الطباعة", ["أوفست (Offset)", "ديجيتال (Digital)"])
        qty = st.number_input("العدد", value=1000, step=100, key="pdf_qty")

with tab2:
    st.subheader("الإدخال اليدوي التقليدي")
    m_col1, m_col2, m_col3 = st.columns(3)
    L_in = m_col1.number_input("الطول (L)", value=20.0)
    W_in = m_col2.number_input("العرض (W)", value=15.0)
    H_in = m_col3.number_input("الارتفاع (H)", value=5.0)

# 7. منطق الحسابات (Engine)
if st.button("🚀 احسب التكلفة الآن"):
    # تحديد القياسات المفتوحة
    if file_body and file_paper:
        bw, bh = get_pdf_dim(file_body.read())
        pw, ph = get_pdf_dim(file_paper.read())
        st.success(f"✅ تم القراءة: الكارتون {bw}x{bh} سم | الورق {pw}x{ph} سم")
    else:
        # حساب يدوي بناءً على نوع العلبة
        extra = 6 if "قطعتين" in b_type else 9
        bw, bh = L_in + (H_in * 2), W_in + (H_in * 2)
        pw, ph = bw + extra, bh + extra

    # حساب عدد القطع بالطبقة
    b_per = max((70 // bw) * (100 // bh), (100 // bw) * (70 // bh))
    is_dig = "Digital" in pr_type
    if is_dig:
        p_per = max((33 // pw) * (70 // ph), (70 // pw) * (33 // ph))
    else:
        p_per = max((70 // pw) * (100 // ph), (100 // pw) * (70 // ph))

    if b_per > 0 and p_per > 0:
        # الحسابات المالية (نفس معادلاتك السابقة لضمان الدقة)
        total_b = math.ceil(qty / b_per)
        total_p = math.ceil(qty / p_per)
        m_cost = (total_b * st.session_state.p_b) + (total_p * st.session_state.p_p)
        f_cost = st.session_state.c_d + st.session_state.c_t + st.session_state.labor
        
        if is_dig:
            w_cost = total_p * st.session_state.dig_p
            w_cost += (math.ceil(total_p / 1300) * (st.session_state.s_l + st.session_state.s_c))
        else:
            f_cost += st.session_state.c_z
            sets = math.ceil((total_p * 2) / 1300)
            w_cost = sets * (st.session_state.s_p + st.session_state.s_l + st.session_state.s_c)

        total = m_cost + w_cost + f_cost
        
        # العرض
        c1, c2 = st.columns(2)
        with c1: st.metric("سعر المفرد", f"{round(total/qty)} دينار")
        with c2: st.metric("الإجمالي", f"{format(total, ',')} دينار")
        
        # التقرير
        st.divider()
        st.markdown("### 📑 تقرير المطبعة")
        col_rep1, col_rep2 = st.columns(2)
        col_rep1.info(f"📦 المواد:\n- كارتون: {total_b} طبقة\n- ورق: {total_p} طبقة\n- قطع/طبقة: {b_per}")
        col_rep2.info(f"🛠️ العمليات:\n- نوع الطباعة: {pr_type}\n- أجور العمل: {format(w_cost, ',')} د.ع")
    else:
        st.error("⚠️ القياسات كبيرة جداً على الخامات!")

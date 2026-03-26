import streamlit as st
import math
import os
import fitz  # مكتبة PyMuPDF لقراءة الـ PDF (لا تنسى تضيفها بـ requirements.txt)

# 1. إعداد الواجهة
st.set_page_config(page_title="نظام تسعير الورشة | Rigid Box Calculator", layout="wide")

PASSWORD = "ULBE2026"
def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center; color: white;'>🔐 النظام مغلق / Sistem Kilitli</h2>", unsafe_allow_html=True)
        pwd = st.text_input("كلمة المرور / Şifre", type="password")
        if st.button("دخول / Giriş"):
            if pwd == PASSWORD: st.session_state["password_correct"] = True; st.rerun()
            else: st.error("❌ كلمة مرور خاطئة")
        return False
    return True

if not check_password(): st.stop()

# إدارة الأسعار الافتراضية
default_prices = {"p_b": 1200, "p_p": 235, "s_p": 40000, "s_l": 60000, "s_c": 130000, "c_d": 100000, "c_z": 30000, "c_t": 25000, "m_p": 500, "labor": 50000, "dig_p": 1500}
for k, v in default_prices.items():
    if k not in st.session_state: st.session_state[k] = v

def reset_prices():
    for k, v in default_prices.items(): st.session_state[k] = v

# القاموس المبسط (عربي فقط للاختصار بهذا المثال، لكنه يدعم التركي كما في السابق)
ln = {
    "title": "نظام التسعير الذكي (قارئ PDF)", "settings": "🛠️ الإعدادات", "calc_btn": "🚀 احسب التكلفة"
}

st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
    h1 { text-align: center; font-size: 26px !important; border-bottom: 1px solid #30363d; padding-bottom: 10px; color: #ffffff;}
    [data-testid="stMetricValue"] { color: #00ff41 !important; font-size: 32px !important; }
    .stButton>button { width: 100%; background-color: #238636; color: white; font-weight: bold; height: 3.5em; border-radius: 8px; border: none;}
    .stButton>button:hover { background-color: #2ea043; }
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

if os.path.exists("logo.png"):
    col1, col2, col3 = st.columns([2, 1, 2])
    with col2: st.image("logo.png", use_container_width=True)

st.title(ln["title"])

# الإعدادات الجانبية
with st.sidebar:
    st.markdown("### 🛠️ الأسعار")
    if st.button("🔄 إعادة ضبط"): reset_prices(); st.rerun()
    st.session_state.p_b = st.number_input("الكارتون", value=st.session_state.p_b)
    st.session_state.p_p = st.number_input("الورق", value=st.session_state.p_p)
    st.session_state.s_p = st.number_input("أجور الطبع", value=st.session_state.s_p)
    st.session_state.s_l = st.number_input("السلفنة", value=st.session_state.s_l)
    st.session_state.s_c = st.number_input("التقطيع", value=st.session_state.s_c)
    st.session_state.dig_p = st.number_input("ورقة الديجيتال", value=st.session_state.dig_p)
    st.session_state.labor = st.number_input("العمال", value=st.session_state.labor)
    st.session_state.c_d = st.number_input("قالب التقطيع", value=st.session_state.c_d)
    st.session_state.c_z = st.number_input("الزنك", value=st.session_state.c_z)
    st.session_state.c_t = st.number_input("النقليات", value=st.session_state.c_t)

# --- دالة قراءة الـ PDF ---
def parse_pdf_dimensions(file_bytes):
    try:
        doc = fitz.open(stream=file_bytes, filetype="pdf")
        page = doc[0]
        drawings = page.get_drawings()
        
        red_rects, yellow_rects = [], []
        
        # البحث عن الألوان في المسارات
        for path in drawings:
            color = path.get("color") # لون الخط (Stroke)
            if color:
                # تقريب قيم الألوان (الـ PDF يستخدم قيم بين 0 و 1)
                r, g, b = [round(c, 1) for c in color]
                if r > 0.8 and g < 0.2 and b < 0.2: # خط أحمر (كارتون)
                    red_rects.append(path["rect"])
                elif r > 0.8 and g > 0.8 and b < 0.2: # خط أصفر (ورق)
                    yellow_rects.append(path["rect"])
        
        # إذا وجدنا مسارات، نحسب أكبر مستطيل محيط بها (Bounding Box)
        # نقطة الـ PDF تساوي 1/72 من الإنش (للتحويل للسم نقسم على 28.346)
        PT_TO_CM = 28.346
        
        bw, bh, pw, ph = 0, 0, 0, 0
        if red_rects:
            r_rect = fitz.Rect(red_rects[0])
            for r in red_rects: r_rect |= r # دمج المستطيلات
            bw = r_rect.width / PT_TO_CM
            bh = r_rect.height / PT_TO_CM
            
        if yellow_rects:
            y_rect = fitz.Rect(yellow_rects[0])
            for y in yellow_rects: y_rect |= y
            pw = y_rect.width / PT_TO_CM
            ph = y_rect.height / PT_TO_CM
            
        return round(bw, 1), round(bh, 1), round(pw, 1), round(ph, 1)
    except Exception as e:
        return None, None, None, None

# --- واجهة الإدخال المدمجة ---
st.markdown("### 📄 إدخال القياسات (آلي أو يدوي)")
uploaded_pdf = st.file_uploader("ارفع ملف الداي كت (PDF - مقياس 1:1, خط أحمر للكارتون، أصفر للورق)", type="pdf")

col1, col2 = st.columns(2)
with col1:
    b_t = st.selectbox("نوع العلبة", ["علبة وقبغ (قطعتين)", "علبة مغناطيسية", "علبة جرارة"])
    pr_t = st.selectbox("نوع الطباعة", ["أوفست (Offset)", "ديجيتال (Digital 33x70)"])
    q = st.number_input("العدد المطلوب", value=1000, step=100)

# المتغيرات الأساسية للقياسات المفتوحة
bw_final, bh_final, pw_final, ph_final = 0, 0, 0, 0
is_pdf_loaded = False

if uploaded_pdf:
    bw_pdf, bh_pdf, pw_pdf, ph_pdf = parse_pdf_dimensions(uploaded_pdf.read())
    if bw_pdf and pw_pdf:
        st.success(f"✅ تم سحب القياسات بنجاح من الـ PDF! (الكارتون: {bw_pdf}x{bh_pdf} سم | الورق: {pw_pdf}x{ph_pdf} سم)")
        bw_final, bh_final = bw_pdf, bh_pdf
        pw_final, ph_final = pw_pdf, ph_pdf
        is_pdf_loaded = True
    else:
        st.error("❌ لم يتم العثور على خطوط (Vector) باللون الأحمر أو الأصفر بشكل صحيح. يرجى التأكد من التصميم أو استخدام الإدخال اليدوي.")

if not is_pdf_loaded:
    with col2:
        st.info("✍️ إدخال يدوي (تجاوز الـ PDF)")
        L = st.number_input("الطول الداخلي (L)", value=26.0)
        W = st.number_input("العرض الداخلي (W)", value=17.0)
        H = st.number_input("الارتفاع الداخلي (H)", value=4.0)
        
        extra = 6 if "قطعتين" in b_t else 9
        bw_final, bh_final = L + (H * 2), W + (H * 2)
        pw_final, ph_final = bw_final + extra, bh_final + extra

st.markdown("<br>", unsafe_allow_html=True)

# --- محرك الحسابات ---
def engine_flat(bw, bh, pw, ph, print_type):
    b_per = max((70 // bw) * (100 // bh), (100 // bw) * (70 // bh))
    is_digital = "Digital" in print_type
    if is_digital:
        p_per = max((33 // pw) * (70 // ph), (70 // pw) * (33 // ph))
    else:
        p_per = max((70 // pw) * (100 // ph), (100 // pw) * (70 // ph))
    return b_per, p_per, is_digital

if st.button(ln["calc_btn"]):
    b_per, p_per, is_digital = engine_flat(bw_final, bh_final, pw_final, ph_final, pr_t)
    
    if b_per > 0 and p_per > 0:
        total_b = math.ceil(q / b_per)
        total_p = math.ceil(q / p_per)
        
        m_cost = (total_b * st.session_state.p_b) + (total_p * st.session_state.p_p)
        f_cost = st.session_state.c_d + st.session_state.c_t + st.session_state.labor
        
        if is_digital:
            w_cost = total_p * st.session_state.dig_p
            sets = math.ceil(total_p / 1300)
            w_cost += (sets * (st.session_state.s_l + st.session_state.s_c))
        else:
            f_cost += st.session_state.c_z
            pr_50x70 = total_p * 2
            sets = math.ceil(pr_50x70 / 1300)
            w_cost = sets * (st.session_state.s_p + st.session_state.s_l + st.session_state.s_c)

        total = m_cost + w_cost + f_cost
        
        c1, c2 = st.columns(2)
        c1.metric("سعر العلبة الواحدة", f"{round(total/q)} IQD")
        c2.metric("الإجمالي الكلي", f"{format(total, ',')} IQD")
        
        st.info(f"الإنتاج: الكارتون ({b_per} بالطبقة) | الورق ({p_per} بالطبقة/الطبعة)")
    else:
        st.error("❌ القياس المفتوح المستخرج أكبر من حجم الطبقة/الطبعة!")

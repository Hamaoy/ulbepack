import streamlit as st
import math
import os

# 1. إعداد واجهة البرنامج
st.set_page_config(page_title="نظام تسعير الورشة الخاص", layout="wide")

# 2. نظام الحماية بكلمة المرور
PASSWORD = "ULBE2026"

def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center;'>🔐 نظام التسعير مغلق</h2>", unsafe_allow_html=True)
        pwd = st.text_input("أدخل كلمة المرور للدخول", type="password")
        if st.button("دخول"):
            if pwd == PASSWORD:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ كلمة المرور غير صحيحة")
        return False
    return True

if not check_password():
    st.stop()

# 3. تصميم الـ CSS (نعومة الخطوط والوضوح)
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
    .logo-container { display: flex; justify-content: center; margin-bottom: 10px; }
    h1 { color: #ffffff !important; font-size: 24px !important; text-align: center; font-weight: 400 !important; border-bottom: 1px solid #30363d; padding-bottom: 15px; }
    [data-testid="stMetricValue"] { color: #00ff41 !important; font-size: 28px !important; }
    .stButton>button { width: 100%; background-color: #238636; color: white; border-radius: 6px; height: 3em; border: none; }
    .stTable { background-color: #161b22; border-radius: 8px; }
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

# استدعاء الشعار إذا وجد (logo.png)
if os.path.exists("logo.png"):
    st.markdown('<div class="logo-container">', unsafe_allow_html=True)
    st.image("logo.png", width=120)
    st.markdown('</div>', unsafe_allow_html=True)

st.title("نظام التسعير الذكي للكرتون المقوى")

# 4. الإعدادات الجانبية (الثوابت)
with st.sidebar:
    st.markdown("### 🛠️ إعدادات التكاليف")
    p_board = st.number_input("سعر طبقة الكارتون (70x100)", value=1200)
    p_paper = st.number_input("سعر طبقة الورق (70x100)", value=235)
    st.divider()
    st.markdown("### 🎨 أجور الوجبة (لحد 1300)")
    s_print = st.number_input("أجور الطبع", value=40000)
    s_lam = st.number_input("أجور السلفنة", value=60000)
    s_cut_lab = st.number_input("أجور التقطيع", value=130000)
    st.divider()
    st.markdown("### 🏗️ القوالب والنقل")
    c_die = st.number_input("قالب التقطيع", value=100000)
    c_zinco = st.number_input("قالب الطباعة (زنك)", value=30000)
    c_trans = st.number_input("النقليات", value=25000)
    st.divider()
    mag_p = st.number_input("سعر زوج المغناطيس", value=500)

# 5. واجهة الإدخال
col1, col2 = st.columns(2)
with col1:
    st.markdown("### 📦 الطلبية")
    box_type = st.selectbox("نوع العلبة", ["علبة وقبغ (قطعتين)", "علبة مغناطيسية", "علبة جرارة"])
    qty = st.number_input("العدد المطلوب", value=1000, step=100)
    use_mag = st.checkbox("إضافة مغناطيس؟")

with col2:
    st.markdown("### 📐 القياسات (سم)")
    lc, wc, hc = st.columns(3)
    with lc: L = st.number_input("الطول", value=26.0)
    with wc: W = st.number_input("العرض", value=17.0)
    with hc: H = st.number_input("الارتفاع", value=4.0)

calc_btn = st.button("🚀 احسب الآن")

# 6. محرك الحسابات
def run_calc(l, w, h, q):
    # إضافات الداي كت بناءً على النوع
    extra = 6 if box_type == "علبة وقبغ (قطعتين)" else 9
    bw, bh = l + (h * 2), w + (h * 2)
    pw, ph = bw + extra, bh + extra
    
    # التوزيع
    b_per = (70 // bw) * (100 // bh)
    p_half = (50 // pw) * (70 // ph)
    p_full = p_half * 2
    
    if b_per == 0 or p_full == 0: return None

    total_b = math.ceil(q / b_per)
    total_p = math.ceil(q / p_full)
    
    # وجبات الطبع (شرط الـ 1300)
    pr_50x70 = total_p * 2 
    sets = math.ceil(pr_50x70 / 1300)
    
    m_cost = (total_b * p_board) + (total_p * p_paper)
    w_cost = (sets * (s_print + s_lam + s_cut_lab))
    f_cost = c_die + c_zinco + c_trans + (q * mag_p if use_mag else 0)
    
    return (m_cost + w_cost + f_cost), b_per, total_b, total_p, pr_50x70, sets, m_cost, w_cost, f_cost

if calc_btn:
    res = run_calc(L, W, H, qty)
    if res:
        total, b_p, b_s, p_s, p_50, sets, cm, cw, cf = res
        
        c_res1, c_res2 = st.columns(2)
        c_res1.metric("سعر العلبة الواحدة", f"{round(total/qty)} د.ع")
        c_res2.metric("الإجمالي الكلي", f"{format(total, ',')} د.ع")

        st.markdown("### 📑 التقرير الفني")
        tc1, tc2 = st.columns(2)
        with tc1:
            st.markdown(f"- كارتون (70x100): **{b_s}** طبقة\n- ورق (70x100): **{p_s}** طبقة")
        with tc2:
            st.markdown(f"- ورق طبع (50x70): **{p_50}** ورقة\n- عدد الوجبات: **{sets}** وجبة")

        with st.expander("تفاصيل التكاليف"):
            st.table({
                "البند": ["المواد", "أجور العمل", "القوالب والثوابت"],
                "المبلغ": [format(cm, ','), format(cw, ','), format(cf, ',')]
            })

        # نصيحة التوفير
        for i in range(1, 11):
            tr = run_calc(L - (i*0.1), W, H, qty)
            if tr and tr[1] > b_p:
                st.warning(f"💡 نصيحة: تقليل الطول {i} ملم يزيد الإنتاج لـ {tr[1]} قطع بالطبقة.")
                break

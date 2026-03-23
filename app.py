import streamlit as st
import math

# إعداد واجهة البرنامج بتصميم ليلي احترافي
st.set_page_config(page_title="حاسبة الورشة الذكية", layout="wide")

# تصميم الـ CSS لتحسين المظهر والألوان
st.markdown("""
    <style>
    /* خلفية التطبيق */
    .stApp { background-color: #0e1117; color: #ffffff; }
    
    /* تنسيق البطاقات (النتائج) */
    [data-testid="stMetricValue"] { color: #00ff41 !important; font-size: 35px !important; }
    [data-testid="stMetricLabel"] { color: #ffffff !important; font-size: 18px !important; }
    
    /* تنسيق العناوين */
    h1, h2, h3 { color: #f1f1f1 !important; border-bottom: 2px solid #007bff; padding-bottom: 10px; }
    
    /* تنسيق الأزرار */
    .stButton>button { 
        width: 100%; 
        background-color: #007bff; 
        color: white; 
        border-radius: 10px; 
        height: 3.5em; 
        font-size: 20px;
        font-weight: bold;
        border: none;
    }
    .stButton>button:hover { background-color: #0056b3; border: 1px solid #ffffff; }
    
    /* تنبيهات التوفير */
    .stAlert { background-color: #1e1e1e; border: 1px solid #ffc107; color: #ffc107; }
    </style>
    """, unsafe_allow_html=True)

# مكان الشعار (Header)
col_logo, col_title = st.columns([1, 4])
with col_logo:
    # هنا سيتم وضع صورة الشعار لاحقاً
    st.markdown("### 🛠️ لوغو الورشة") 
with col_title:
    st.title("نظام التسعير الذكي - Rigid Box Calculator")

# --- الإعدادات الجانبية (Sidebar) ---
with st.sidebar:
    st.header("📝 تكاليف المواد الخام")
    p_board = st.number_input("سعر طبقة الكارتون (70x100)", value=1200)
    p_paper = st.number_input("سعر طبقة الورق (70x100)", value=235)
    st.divider()
    st.header("⚙️ أجور العمليات (للوجبة)")
    s_print = st.number_input("سعر الطبع (لحد 1300)", value=40000)
    s_lam = st.number_input("سعر السلفنة (لحد 1300)", value=60000)
    s_cut = st.number_input("أجور التقطيع (لحد 1300)", value=130000)
    st.divider()
    fixed_extra = st.number_input("قوالب + نقل + ثابتة", value=155000)

# --- مدخلات الزبون ---
c1, c2 = st.columns(2)
with c1:
    st.markdown("### 📦 تفاصيل الطلب")
    box_type = st.selectbox("نوع العلبة", ["علبة وقبغ (قطعتين)", "علبة مغناطيسية", "علبة جرارة"])
    qty = st.number_input("العدد المطلوب", value=1000, step=100)
    use_magnet = st.checkbox("إضافة مغناطيس؟")
    magnet_p = st.number_input("سعر المغناطيس (للقطعة)", value=500) if use_magnet else 0

with c2:
    st.markdown("### 📐 القياسات (سم)")
    l_col, w_col, h_col = st.columns(3)
    with l_col: L = st.number_input("الطول", value=26.0)
    with w_col: W = st.number_input("العرض", value=17.0)
    with h_col: H = st.number_input("الارتفاع", value=4.0)

st.write("") # مسافة
calculate_btn = st.button("🚀 احسب التكلفة النهائية")

# --- محرك الحسابات ---
def run_calc(l, w, h, q):
    # تقدير الداي كت (مستوحى من ملفاتك)
    extra = 6 if box_type == "علبة وقبغ (قطعتين)" else 9
    bw, bh = l + (h * 2), w + (h * 2)
    pw, ph = bw + extra, bh + extra
    
    b_per_s = (70 // bw) * (100 // bh)
    p_per_half = (50 // pw) * (70 // ph)
    p_per_full = p_per_half * 2
    
    if b_per_s == 0 or p_per_full == 0: return None

    total_b = math.ceil(q / b_per_s)
    total_p = math.ceil(q / p_per_full)
    printed_50x70 = total_p * 2 
    sets = math.ceil(printed_50x70 / 1300)
    
    cost_m = (total_b * p_board) + (total_p * p_paper)
    cost_v = (sets * (s_print + s_lam + s_cut))
    cost_f = fixed_extra + (q * magnet_p)
    
    return (cost_m + cost_v + cost_f), b_per_s, total_b, total_p, printed_50x70, sets

if calculate_btn:
    res = run_calc(L, W, H, qty)
    if res:
        total, b_per_s, b_sh, p_sh, p_50x70, sets = res
        
        # عرض النتائج الكبرى بوضوح عالي
        r1, r2 = st.columns(2)
        r1.metric("السعر الصافي للعلبة", f"{round(total/qty)} دينار")
        r2.metric("إجمالي الفاتورة", f"{format(total, ',')} دينار")

        # تقرير المطبعة
        st.markdown("### 📑 تقرير المطبعة (كشف الحساب)")
        t1, t2 = st.columns(2)
        with t1:
            st.info(f"**المواد:**\n- طبقات الكارتون: {b_sh}\n- طبقات الورق: {p_sh}\n

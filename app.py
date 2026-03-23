import streamlit as st
import math

# إعداد الواجهة بتصميم أنيق
st.set_page_config(page_title="نظام تسعير الورشة", layout="wide")

# تصميم الـ CSS لتحسين المظهر ونعومة الخطوط
st.markdown("""
    <style>
    /* خلفية داكنة واحترافية */
    .stApp { background-color: #0e1117; color: #e0e0e0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
    
    /* تنعيم العناوين */
    h1 { color: #ffffff !important; font-size: 28px !important; font-weight: 500 !important; border-bottom: 1px solid #30363d; padding-bottom: 15px; margin-bottom: 25px; }
    h2, h3 { color: #ffffff !important; font-size: 20px !important; font-weight: 400 !important; margin-top: 20px; }
    
    /* تنسيق كروت النتائج */
    [data-testid="stMetricValue"] { color: #00ff41 !important; font-size: 30px !important; font-weight: 600 !important; }
    [data-testid="stMetricLabel"] { color: #8b949e !important; font-size: 16px !important; }
    
    /* زر الحساب */
    .stButton>button { 
        width: 100%; 
        background-color: #238636; 
        color: white; 
        border-radius: 6px; 
        height: 3em; 
        font-size: 18px;
        border: none;
        transition: 0.3s;
    }
    .stButton>button:hover { background-color: #2ea043; box-shadow: 0 4px 12px rgba(46,160,67,0.3); }
    
    /* الجداول والتنبيهات */
    .stTable { background-color: #161b22; border-radius: 8px; }
    .stAlert { background-color: #161b22; border: 1px solid #d29922; color: #e3b341; border-radius: 8px; }
    
    /* إخفاء شعار سترمليت لزيادة الرسمية */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

st.title("نظام التسعير الذكي للكرتون المقوى")

# --- الإعدادات الجانبية (الأرقام الثابتة) ---
with st.sidebar:
    st.markdown("### 🛠️ الأسعار المرجعية")
    p_board = st.number_input("سعر طبقة الكارتون (70x100)", value=1200)
    p_paper = st.number_input("سعر طبقة الورق (70x100)", value=235)
    
    st.divider()
    st.markdown("### 🎨 أجور الوجبة (لحد 1300)")
    s_print = st.number_input("أجور الطبع", value=40000)
    s_lam = st.number_input("أجور السلفنة", value=60000)
    s_cut_labor = st.number_input("أجور ماكينة التقطيع", value=130000)
    
    st.divider()
    st.markdown("### 🏗️ القوالب والنقل")
    cost_die_mold = st.number_input("قالب التقطيع (كارتون+ورق)", value=100000)
    cost_print_plates = st.number_input("قالب الطباعة (زنك)", value=30000)
    cost_transport = st.number_input("النقليات الداخلية", value=25000)
    
    st.divider()
    magnet_price = st.number_input("سعر زوج المغناطيس", value=500)

# --- واجهة الإدخال الرئيسية ---
col_main1, col_main2 = st.columns(2)

with col_main1:
    st.markdown("### 📦 تفاصيل الطلب")
    box_type = st.selectbox("نوع العلبة", ["علبة وقبغ (قطعتين)", "علبة مغناطيسية", "علبة جرارة"])
    qty = st.number_input("العدد المطلوب", value=1000, step=100)
    use_magnet = st.checkbox("إضافة مغناطيس؟")

with col_main2:
    st.markdown("### 📐 القياسات (سم)")
    l_c, w_c, h_c = st.columns(3)
    with l_c: L = st.number_input("الطول", value=26.0)
    with w_c: W = st.number_input("العرض", value=17.0)
    with h_c: H = st.number_input("الارتفاع", value=4.0)

st.markdown("<br>", unsafe_allow_html=True)
calculate_btn = st.button("🚀 احسب الآن")

# --- محرك الحسابات ---
def run_calculation(l, w, h, q):
    # إضافات الداي كت
    extra = 6 if box_type == "علبة وقبغ (قطعتين)" else 9
    bw, bh = l + (h * 2), w + (h * 2)
    pw, ph = bw + extra, bh + extra
    
    # التوزيع
    b_per_s = (70 // bw) * (100 // bh)
    p_per_half = (50 // pw) * (70 // ph)
    p_per_full = p_per_half * 2
    
    if b_per_s == 0 or p_per_full == 0: return None

    total_b = math.ceil(q / b_per_s)
    total_p = math.ceil(q / p_per_full)
    
    # وجبات الطبع (شرط الـ 1300)
    printed_50x70 = total_p * 2 
    sets = math.ceil(printed_50x70 / 1300)
    
    # مبالغ
    m_cost = (total_b * p_board) + (total_p * p_paper)
    w_cost = (sets * (s_print + s_lam + s_cut_labor))
    f_cost = cost_die_mold + cost_print_plates + cost_transport
    if use_magnet: f_cost += (q * magnet_price)
    
    total = m_cost + w_cost + f_cost
    return total, b_per_s, total_b, total_p, printed_50x70, sets, m_cost, w_cost, f_cost

if calculate_btn:
    res = run_calculation(L, W, H, qty)
    if res:
        total, b_per_s, b_sh, p_sh, p_50x70, sets, c_m, c_w, c_f = res
        
        # النتائج الأساسية
        res_col1, res_col2 = st.columns(2)
        res_col1.metric("سعر العلبة الواحدة", f"{round(total/qty)} د.ع")
        res_col2.metric("الإجمالي الكلي", f"{format(total, ',')} د.ع")

        # تقرير المطبعة
        st.markdown("### 📑 التقرير الفني")
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            st.markdown(f"""
            - كارتون (70x100): **{b_sh}** طبقة
            - ورق (70x100): **{p_sh}** طبقة
            - استخراج العلب: **{b_per_s}** بالطبقة
            """)
        with t_col2:
            st.markdown(f"""
            - ورق طبع (50x70): **{p_50x70}** ورقة
            - عدد الوجبات: **{sets}** وجبة
            - كلفة العمل: **{format(c_w, ',')}** د.ع
            """)

        # تفصيل التكاليف الثابتة
        with st.expander("تفاصيل بنود التكلفة"):
            st.table({
                "البند": ["المواد الخام", "أجور العمليات", "القوالب", "النقليات والزنك"],
                "المبلغ (دينار)": [format(c_m, ','), format(c_w, ','), format(cost_die_mold, ','), format(cost_print_plates + cost_transport, ',')]
            })

        # نصيحة التوفير
        for i in range(1, 11):
            t_res = run_calculation(L - (i*0.1), W, H, qty)
            if t_res and t_res[1] > b_per_s:
                st.warning(f"💡 نصيحة: تقليل **الطول** بمقدار {i} ملم يزيد الإنتاج لـ {t_res[1]} علب بالطبقة.")
                break

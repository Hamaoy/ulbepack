import streamlit as st
import math

# إعداد واجهة البرنامج
st.set_page_config(page_title="حاسبة Rigid Box الاحترافية", layout="wide")

# تجميل التصميم باستخدام CSS بسيط
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; box-shadow: 0 2px 4px rgba(0,0,0,0.05); }
    .stButton>button { width: 100%; background-color: #007bff; color: white; border-radius: 8px; height: 3em; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

st.title("📦 نظام التسعير الذكي والمطور")
st.info("هذا النظام يحسب التكاليف بناءً على نظام الوجبات (1300 ورقة للوجبة الواحدة).")

# --- الإعدادات الجانبية ---
with st.sidebar:
    st.header("⚙️ الأسعار والعمليات")
    p_board = st.number_input("سعر طبقة الكارتون (70x100)", value=1200)
    p_paper = st.number_input("سعر طبقة الورق (70x100)", value=235)
    st.divider()
    s_print = st.number_input("سعر وجبة الطبع", value=40000)
    s_lamination = st.number_input("سعر وجبة السلفنة", value=60000)
    s_cutting = st.number_input("أجور التقطيع (للوجبة)", value=130000)
    st.divider()
    magnet_price = st.number_input("سعر زوج المغناطيس", value=500)
    fixed_extra = st.number_input("مصاريف أخرى (قوالب + نقل)", value=155000)

# --- مدخلات البيانات ---
col1, col2 = st.columns([1, 1])

with col1:
    st.subheader("📋 تفاصيل الطلبية")
    box_type = st.selectbox("نوع العلبة", ["علبة وقبغ (قطعتين)", "علبة مغناطيسية", "علبة جرارة"])
    qty = st.number_input("العدد المطلوب (علبة)", value=1000, step=100)
    use_magnet = st.checkbox("إضافة مغناطيس؟")

with col2:
    st.subheader("📐 القياسات الصافية (سم)")
    c_l, c_w, c_h = st.columns(3)
    with c_l: L = st.number_input("الطول", value=26.0)
    with c_w: W = st.number_input("العرض", value=17.0)
    with c_h: H = st.number_input("الارتفاع", value=4.0)

st.divider()

# زر الحساب الأساسي
calculate_btn = st.button("🚀 احسب التكلفة التفصيلية")

# --- المحرك الحسابي ---
def calculate_engine(l, w, h, q):
    # تقدير الداي كت
    extra = 6 if box_type == "علبة وقبغ (قطعتين)" else 9
    b_w, b_h = l + (h * 2), w + (h * 2)
    p_w, p_h = b_w + extra, b_h + extra
    
    # التوزيع
    b_per_s = (70 // b_w) * (100 // b_h)
    p_per_half = (50 // p_w) * (70 // p_h)
    p_per_full = p_per_half * 2
    
    if b_per_s == 0 or p_per_full == 0: return None

    total_b_sheets = math.ceil(q / b_per_s)
    total_p_sheets = math.ceil(q / p_per_full)
    
    # حساب الوجبات (1300)
    actual_printed_50x70 = total_p_sheets * 2 
    num_sets = math.ceil(actual_printed_50x70 / 1300)
    
    # التكاليف
    cost_mats = (total_b_sheets * p_board) + (total_p_sheets * p_paper)
    cost_vars = (num_sets * (s_print + s_lamination + s_cutting))
    cost_fixed = fixed_extra + (q * magnet_price if use_magnet else 0)
    
    total = cost_mats + cost_vars + cost_fixed
    return total, b_per_s, total_b_sheets, total_p_sheets, actual_printed_50x70, num_sets

if calculate_btn:
    res = calculate_engine(L, W, H, qty)
    if res:
        total_price, b_per_s, b_sheets, p_sheets, printed_50x70, sets = res
        
        # عرض النتائج الكبيرة
        c1, c2 = st.columns(2)
        with c1:
            st.metric("السعر النهائي للعلبة", f"{round(total_price/qty)} دينار")
        with c2:
            st.metric("إجمالي مبلغ الفاتورة", f"{format(total_price, ',')} دينار")

        # --- كشف الحساب التفصيلي ---
        st.subheader("📑 كشف حساب (تقرير المطبعة)")
        
        t_col1, t_col2 = st.columns(2)
        with t_col1:
            st.markdown(f"""
            **المواد الأولية:**
            * عدد طبقات الكارتون (70x100): **{b_sheets}** طبقة.
            * عدد طبقات الورق (70x100): **{p_sheets}** طبقة.
            * العلب المستخرجة من طبقة كارتون واحدة: **{b_per_s}** علبة.
            """)
        
        with t_col2:
            st.markdown(f"""
            **العمليات الفنية:**
            * عدد أوراق الطبع (50x70): **{printed_50x70}** ورقة.
            * عدد الوجبات المحسوبة (طبع/سلفنة): **{sets}** وجبة.
            * (الوجبة الواحدة تغطي لحد 1300 ورقة 50x70).
            """)

        # --- جدول التكاليف ---
        st.table({
            "البند": ["تكلفة الكارتون", "تكلفة الورق", "أجور الطبع والسلفنة والقص", "إضافات (مغناطيس/قوالب/نقل)"],
            "المبلغ (دينار)": [
                format(b_sheets * p_board, ','),
                format(p_sheets * p_paper, ','),
                format(sets * (s_print + s_lamination + s_cutting), ','),
                format(fixed_extra + (qty * magnet_price if use_magnet else 0), ',')
            ]
        })

        # --- نصيحة التوفير ---
        st.divider()
        st.subheader("💡 نصيحة التوفير الذكية")
        found = False
        for i in range(1, 11):
            test_l = L - (i*0.1)
            t_res = calculate_engine(test_l, W, H, qty)
            if t_res and t_res[1] > b_per_s:
                st.warning(f"إذا قللت **الطول** بمقدار {i} ملم، ستخرج {t_res[1]} علب من الطبقة بدلاً من {b_per_s}. ستوفر مبلقاً كبيراً!")
                found = True
                break
        if not found: st.success("قياساتك الحالية مستغلة لمساحة الكارتون بأفضل شكل.")

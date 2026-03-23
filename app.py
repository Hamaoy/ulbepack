import streamlit as st
import math

st.set_page_config(page_title="حاسبة Rigid Box الاحترافية", layout="wide")
st.title("📦 نظام التسعير الذكي - نسخة الوجبات المرنة")

# --- الإعدادات الجانبية ---
with st.sidebar:
    st.header("⚙️ الأسعار الأساسية")
    p_board = st.number_input("سعر طبقة الكارتون (70x100)", value=1200)
    p_paper = st.number_input("سعر طبقة الورق (70x100)", value=235)
    st.divider()
    s_print = st.number_input("سعر وجبة الطبع (لحد 1300 ورقة)", value=40000)
    s_lamination = st.number_input("سعر وجبة السلفنة (لحد 1300 ورقة)", value=60000)
    s_cutting_labor = st.number_input("أجور التقطيع (لحد 1300 ورقة)", value=130000)
    st.divider()
    magnet_price = st.number_input("سعر زوج المغناطيس + التركيب", value=500)

# --- مدخلات الطلبية ---
col_a, col_b = st.columns(2)
with col_a:
    box_type = st.selectbox("نوع العلبة", ["علبة وقبغ (قطعتين)", "علبة مغناطيسية", "علبة جرارة"])
    qty = st.number_input("العدد المطلوب (علبة)", value=1000, step=100)
    use_magnet = st.checkbox("إضافة مغناطيس؟")

with col_b:
    st.write("📐 قياسات العلبة الصافية (سم)")
    L = st.number_input("الطول", value=26.0)
    W = st.number_input("العرض", value=17.0)
    H = st.number_input("الارتفاع", value=4.0)

# --- محرك الحسابات ---
def calculate_all(l, w, h, q):
    # إضافات الداي كت حسب النوع (تقديرية)
    extra = 6 if box_type == "علبة وقبغ (قطعتين)" else 9
    b_w, b_h = l + (h * 2), w + (h * 2)
    p_w, p_h = b_w + extra, b_h + extra
    
    # حساب التوزيع
    b_per_s = (70 // b_w) * (100 // b_h)
    p_per_half = (50 // p_w) * (70 // p_h)
    p_per_full = p_per_half * 2
    
    if b_per_s == 0 or p_per_full == 0: return None

    total_b_sheets = math.ceil(q / b_per_s)
    total_p_sheets = math.ceil(q / p_per_full)
    
    # حساب الوجبات (بناءً على شرط الـ 1300 ورقة 50x70)
    actual_printed_papers = total_p_sheets * 2 
    num_sets = math.ceil(actual_printed_papers / 1300)
    
    # التكاليف
    c_mats = (total_b_sheets * p_board) + (total_p_sheets * p_paper)
    c_vars = (num_sets * s_print) + (num_sets * s_lamination) + (num_sets * s_cutting_labor)
    c_fixed = 100000 + 30000 + 25000 
    if use_magnet: c_fixed += (q * magnet_price)
    
    total = c_mats + c_vars + c_fixed
    return total, b_per_s, total_b_sheets, actual_printed_papers, num_sets

res = calculate_all(L, W, H, qty)

if res:
    total_price, b_per_s, b_sheets, printed_papers, sets = res
    st.divider()
    st.metric("السعر النهائي للعلبة الواحدة", f"{round(total_price/qty)} دينار")
    
    with st.expander("🔍 تفاصيل الحسبة الفنية"):
        st.write(f"• عدد الوجبات المحسوبة: **{sets}** (بناءً على {printed_papers} ورقة طبع)")
        st.write(f"• العلب بالطبقة الواحدة (الكارتون): **{b_per_s}**")
        st.write(f"• إجمالي طبقات الكارتون المطلوب: **{b_sheets}**")

    # --- المستشار الذكي (فحص الطول والعرض) ---
    st.subheader("💡 مقترحات التوفير")
    optimizations = []
    for i in range(1, 11): # فحص تقليل لحد 10 ملم
        # فحص الطول
        t_res_l = calculate_all(L - (i*0.1), W, H, qty)
        if t_res_l and t_res_l[1] > b_per_s:
            optimizations.append(f"قلل **الطول** بمقدار {i} ملم لزيادة الإنتاج بالطبقة.")
        # فحص العرض
        t_res_w = calculate_all(L, W - (i*0.1), H, qty)
        if t_res_w and t_res_w[1] > b_per_s:
            optimizations.append(f"قلل **العرض** بمقدار {i} ملم لزيادة الإنتاج بالطبقة.")

    if optimizations:
        for opt in set(optimizations): st.warning(opt)
    else:
        st.success("القياسات مستغلة للمساحة بشكل ممتاز.")

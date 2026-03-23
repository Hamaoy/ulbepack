import streamlit as st
import math

# إعدادات الصفحة
st.set_page_config(page_title="حاسبة Rigid Box الذكية", layout="centered")

st.title("📦 نظام تسعير علب الكارتون المقوى")

# مدخلات المستخدم
with st.sidebar:
    st.header("⚙️ إعدادات الأسعار")
    price_board = st.number_input("سعر طبقة الكارتون", value=1200)
    price_paper = st.number_input("سعر طبقة الورق", value=235)
    st.divider()
    cost_print = st.number_input("سعر الطبع (نصف طبقة)", value=40000)
    cost_lamination = st.number_input("سعر السلفنة", value=60000)
    cost_die_cut_plates = st.number_input("سعر قوالب التقطيع", value=100000)

st.subheader("📐 أدخل قياسات العلبة (سم)")
col1, col2, col3 = st.columns(3)
with col1: L = st.number_input("الطول (L)", value=26)
with col2: W = st.number_input("العرض (W)", value=17)
with col3: H = st.number_input("الارتفاع (H)", value=4)

qty = st.number_input("العدد المطلوب", value=1000)

if st.button("احسب التكلفة الآن"):
    # حسابات التوزيع (Nesting Logic)
    # الحوض والقبغ (كارتون) - طبقة كاملة 70x100
    b_w, b_h = L + (H * 2), W + (H * 2)
    board_per_sheet = (70 // b_w) * (100 // b_h)
    
    # الورق - نصف طبقة 50x70
    p_w, p_h = b_w + 6, b_h + 6
    paper_per_half = (50 // p_w) * (70 // p_h)
    
    # حساب الكميات
    total_b_sheets = math.ceil(qty / board_per_sheet) if board_per_sheet > 0 else 0
    total_p_sheets = math.ceil(qty / (paper_per_half * 2)) if paper_per_half > 0 else 0
    
    # حساب المبالغ
    mats_total = (total_b_sheets * price_board) + (total_p_sheets * price_paper)
    fixed_total = cost_print + cost_lamination + cost_die_cut_plates + 30000 + 130000 + 25000
    
    final_cost = mats_total + fixed_total
    
    # عرض النتائج
    st.success(f"سعر العلبة الواحدة: {round(final_cost/qty)} دينار")
    
    st.table({
        "المادة": ["كارتون", "ورق", "أجور ثابتة", "المجموع الكلي"],
        "الكمية/العدد": [total_b_sheets, total_p_sheets, "-", qty],
        "التكلفة (دينار)": [total_b_sheets*price_board, total_p_sheets*price_paper, fixed_total, final_cost]
    })

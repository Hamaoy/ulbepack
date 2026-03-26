import streamlit as st
import math
import os

# 1. إعدادات الصفحة والسمة البصرية (UI)
st.set_page_config(page_title="ULBE Smart System", layout="wide")

# تثبيت الألوان والخلفية لضمان الوضوح على كل الأجهزة
st.markdown("""
    <style>
    .stApp {
        background-color: #0d1117;
        color: #e6edf3;
    }
    [data-testid="stMetricValue"] {
        color: #3fb950 !important;
        font-size: 32px !important;
        font-weight: bold;
    }
    [data-testid="stMetricLabel"] {
        color: #8b949e !important;
    }
    .main-card {
        background-color: #161b22;
        padding: 20px;
        border-radius: 12px;
        border: 1px solid #30363d;
        margin-bottom: 20px;
    }
    h1, h2, h3 {
        color: #58a6ff !important;
    }
    .stButton>button {
        width: 100%;
        background-color: #238636;
        color: white;
        font-weight: bold;
        border: none;
        height: 3em;
    }
    .stButton>button:hover {
        background-color: #2ea043;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. نظام الحماية
PASSWORD = "ULBE2026"
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

def check_password():
    if not st.session_state["authenticated"]:
        st.markdown("<h2 style='text-align: center;'>🔐 نظام تسعير ULBE</h2>", unsafe_allow_html=True)
        pwd = st.text_input("ادخل كلمة المرور", type="password")
        if st.button("دخول"):
            if pwd == PASSWORD:
                st.session_state["authenticated"] = True
                st.rerun()
            else:
                st.error("❌ كلمة المرور غير صحيحة")
        return False
    return True

if not check_password(): st.stop()

# 3. إدارة الأسعار الافتراضية
if 'prices' not in st.session_state:
    st.session_state.prices = {
        "p_b": 1200, "p_p": 250, "dig_p": 1500, "ribbon_p": 300, 
        "labor": 50000, "zinc": 30000, "mold": 100000, "transport": 25000,
        "print_job": 40000, "lamination": 60000, "cutting": 130000
    }

def reset_prices():
    st.session_state.prices = {
        "p_b": 1200, "p_p": 250, "dig_p": 1500, "ribbon_p": 300, 
        "labor": 50000, "zinc": 30000, "mold": 100000, "transport": 25000,
        "print_job": 40000, "lamination": 60000, "cutting": 130000
    }

# 4. الشعار
col_logo_1, col_logo_2, col_logo_3 = st.columns([2, 1, 2])
with col_logo_2:
    if os.path.exists("logo.png"):
        st.image("logo.png", use_container_width=True)
    else:
        st.markdown("<h1 style='text-align: center;'>ULBE</h1>", unsafe_allow_html=True)

# 5. القائمة الجانبية (الإعدادات)
with st.sidebar:
    st.header("🛠️ إعدادات التكاليف")
    if st.button("🔄 إعادة ضبط المصنع"): reset_prices(); st.rerun()
    p = st.session_state.prices
    p["p_b"] = st.number_input("سعر لوح الكارتون", value=p["p_b"])
    p["p_p"] = st.number_input("سعر فرخ الورق", value=p["p_p"])
    p["dig_p"] = st.number_input("سعر طبعة الديجيتال", value=p["dig_p"])
    p["ribbon_p"] = st.number_input("سعر متر الشريط (للـ Kurdele)", value=p["ribbon_p"])
    st.divider()
    p["labor"] = st.number_input("أجور العمال", value=p["labor"])
    p["mold"] = st.number_input("تكلفة القالب", value=p["mold"])

# 6. المحرك الهندسي (Logic) - بناءً على تحليل ملفات الـ PDF الخاصة بك
def calculate_production(L, W, H, b_type):
    parts = []
    # معادلات الإزاحة (Offsets) مستخرجة من ملفاتك (زيادة التغليف 4.5 سم للورق)
    if b_type == "علبة وقبغ (قطعتين)":
        parts.append({"name": "كارتون الحوض", "w": L + (2*H), "h": W + (2*H), "type": "board"})
        parts.append({"name": "كارتون القبغ", "w": (L+0.5) + (2*3), "h": (W+0.5) + (2*3), "type": "board"})
        parts.append({"name": "ورق الحوض", "w": L + (2*H) + 4.5, "h": W + (2*H) + 4.5, "type": "paper"})
        parts.append({"name": "ورق القبغ", "w": (L+0.5) + (2*3) + 4.5, "h": (W+0.5) + (2*3) + 4.5, "type": "paper"})
    
    elif b_type in ["علبة مغناطيسية", "علبة شريط (Kurdele)"]:
        parts.append({"name": "كارتون الحوض", "w": L + (2*H), "h": W + (2*H), "type": "board"})
        parts.append({"name": "كارتون الغلاف (Cover)", "w": (2*L) + (2*H) + 2, "h": W + 1, "type": "board"})
        parts.append({"name": "ورق الحوض", "w": L + (2*H) + 4.5, "h": W + (2*H) + 4.5, "type": "paper"})
        parts.append({"name": "ورق الغلاف الخارجي", "w": (2*L) + (2*H) + 7, "h": W + 5, "type": "paper"})
        parts.append({"name": "البطانة الداخلية (Inner)", "w": (2*L) + (2*H), "h": W, "type": "paper"})

    elif b_type == "علبة جرارة (مجر)":
        parts.append({"name": "كارتون المجر", "w": L + (2*H), "h": W + (2*H), "type": "board"})
        parts.append({"name": "كارتون الكفر (Sleeve)", "w": (2*W) + (2*H) + 2, "h": L, "type": "board"})
        parts.append({"name": "ورق المجر", "w": L + (2*H) + 4.5, "h": W + (2*H) + 4.5, "type": "paper"})
        parts.append({"name": "ورق الكفر الخارجي", "w": (2*W) + (2*H) + 7, "h": L + 4.5, "type": "paper"})
    
    return parts

# 7. واجهة الإدخال
st.title("🚀 حاسبة الإنتاج الذكية")
input_col1, input_col2 = st.columns(2)

with input_col1:
    st.markdown("### 📋 تفاصيل الطلبية")
    box_selection = st.selectbox("نوع العلبة", ["علبة وقبغ (قطعتين)", "علبة مغناطيسية", "علبة شريط (Kurdele)", "علبة جرارة (مجر)"])
    print_method = st.radio("نوع الطباعة", ["أوفست (70x100)", "ديجيتال (33x70)"], horizontal=True)
    order_qty = st.number_input("الكمية المطلوبة", value=1000, step=100)

with input_col2:
    st.markdown("### 📐 القياسات الصافية (سم)")
    l_val = st.number_input("الطول الداخلي (L)", value=20.0)
    w_val = st.number_input("العرض الداخلي (W)", value=15.0)
    h_val = st.number_input("الارتفاع الداخلي (H)", value=5.0)

st.divider()

# 8. تنفيذ الحسابات
if st.button("احسب التكلفة والإنتاج 🔥"):
    box_parts = calculate_production(l_val, w_val, h_val, box_selection)
    
    total_m_cost = 0
    prod_details = []
    
    st.markdown("### 🏭 تفاصيل القص (التحليل الفني)")
    grid = st.columns(len(box_parts))
    
    for i, part in enumerate(box_parts):
        # تحديد حجم ورقة الطباعة بناءً على النوع
        sheet_w, sheet_h = (33, 70) if "ديجيتال" in print_method and part['type'] == "paper" else (70, 100)
        
        # حساب كم قطعة تطلع بالطبقة
        per_sheet = max((sheet_w // part['w']) * (sheet_h // part['h']), (sheet_h // part['w']) * (sheet_w // part['h']))
        
        if per_sheet <= 0:
            st.error(f"⚠️ الجزء [{part['name']}] قياسه ({part['w']}x{part['h']}) أكبر من الورق!")
            continue
            
        needed_sheets = math.ceil(order_qty / per_sheet)
        
        # حساب التكلفة للمواد
        if part['type'] == "board":
            cost = needed_sheets * st.session_state.prices["p_b"]
        else:
            if "ديجيتال" in print_method:
                cost = needed_sheets * st.session_state.prices["dig_p"]
            else:
                cost = needed_sheets * st.session_state.prices["p_p"]
        
        total_m_cost += cost
        
        with grid[i]:
            st.markdown(f"""
            <div style='background:#1c2128; padding:10px; border-radius:8px; border:1px solid #444; text-align:center;'>
                <small style='color:#8b949e;'>{part['name']}</small><br>
                <b style='color:#58a6ff;'>{part['w']}x{part['h']}</b><br>
                <span style='font-size:12px;'>القطع/الطبقة: {int(per_sheet)}</span>
            </div>
            """, unsafe_allow_html=True)

    # تكاليف الشريط (إذا كانت علبة شريط)
    ribbon_cost = 0
    if box_selection == "علبة شريط (Kurdele)":
        ribbon_cost = order_qty * 0.6 * st.session_state.prices["ribbon_p"] # افتراض 60 سم لكل علبة

    # تكاليف العمل والتشغيل
    fixed_costs = st.session_state.prices["mold"] + st.session_state.prices["transport"] + st.session_state.prices["labor"]
    if "أوفست" in print_method:
        fixed_costs += st.session_state.prices["zinc"]
        work_costs = (math.ceil(order_qty/1000)) * (st.session_state.prices["print_job"] + st.session_state.prices["lamination"] + st.session_state.prices["cutting"])
    else:
        work_costs = (math.ceil(order_qty/1000)) * (st.session_state.prices["lamination"] + st.session_state.prices["cutting"])

    total_final = total_m_cost + fixed_costs + work_costs + ribbon_cost
    unit_price = total_final / order_qty

    # 9. عرض النتائج النهائية
    st.divider()
    res_col1, res_col2 = st.columns(2)
    with res_col1:
        st.metric("سعر العلبة الواحدة", f"{round(unit_price)} د.ع")
    with res_col2:
        st.metric("إجمالي مبلغ الطلبية", f"{format(int(total_final), ',')} د.ع")

    st.markdown(f"""
    <div class="main-card">
        <h3 style='margin-top:0;'>📝 ملخص تقرير الإنتاج</h3>
        <table style='width:100%; color:white;'>
            <tr><td>تكلفة المواد الأولية (كارتون وورق):</td><td style='text-align:left;'>{format(int(total_m_cost), ',')} د.ع</td></tr>
            <tr><td>تكلفة الشريط (Ribbon):</td><td style='text-align:left;'>{format(int(ribbon_cost), ',')} د.ع</td></tr>
            <tr><td>أجور العمال والقالب والزنكات:</td><td style='text-align:left;'>{format(int(fixed_costs), ',')} د.ع</td></tr>
            <tr><td>أجور الطبع والسلفنة والتقطيع:</td><td style='text-align:left;'>{format(int(work_costs), ',')} د.ع</td></tr>
            <tr style='color:#3fb950; font-weight:bold; font-size:1.2em;'><td>الإجمالي الكلي:</td><td style='text-align:left;'>{format(int(total_final), ',')} د.ع</td></tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

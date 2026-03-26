import streamlit as st
import math
import os

# 1. إعدادات المظهر (Off-White & Clear Black Text)
st.set_page_config(page_title="ULBE Production Pro", layout="wide")

st.markdown("""
    <style>
    .stApp {
        background-color: #FDFCF8;
        color: #1A1A1A;
    }
    p, span, label, .stMarkdown, .stMetric {
        color: #1A1A1A !important;
        font-weight: 600;
    }
    h1, h2, h3 {
        color: #004E96 !important;
    }
    .stNumberInput input {
        background-color: #FFFFFF !important;
        color: #000000 !important;
        border: 1px solid #CCC !important;
    }
    .result-card {
        background-color: #FFFFFF;
        padding: 20px;
        border-radius: 12px;
        border: 2px solid #004E96;
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    .tip-box {
        background-color: #E3F2FD;
        border-right: 6px solid #2196F3;
        padding: 12px;
        color: #0D47A1 !important;
        margin: 8px 0;
        border-radius: 4px;
        font-size: 14px;
    }
    .stButton>button {
        background-color: #004E96;
        color: white;
        font-weight: bold;
        height: 3.5em;
        width: 100%;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. حماية النظام
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 دخول النظام")
    if st.text_input("كلمة السر", type="password") == "ULBE2026":
        if st.button("دخول"): 
            st.session_state.auth = True
            st.rerun()
    st.stop()

# 3. محرك الحسابات (الأجزاء الهندسية بناءً على ملفاتك)
def get_box_structure(L, W, H, b_type):
    # القياسات المفتوحة مع إزاحات التغليف (4.5 سم للورق)
    if b_type == "علبة وقبغ (قطعتين)":
        return [
            {"n": "كارتون الحوض", "w": L+(2*H), "h": W+(2*H), "t": "b"},
            {"n": "كارتون القبغ", "w": (L+0.5)+(2*3), "h": (W+0.5)+(2*3), "t": "b"},
            {"n": "ورق الحوض", "w": L+(2*H)+4.5, "h": W+(2*H)+4.5, "t": "p"},
            {"n": "ورق القبغ", "w": (L+0.5)+(2*3)+4.5, "h": (W+0.5)+(2*3)+4.5, "t": "p"}
        ]
    elif b_type in ["علبة مغناطيسية", "علبة شريط (Kurdele)"]:
        return [
            {"n": "كارتون الحوض", "w": L+(2*H), "h": W+(2*H), "t": "b"},
            {"n": "كارتون الغلاف", "w": (2*L)+(2*H)+2, "h": W+1, "t": "b"},
            {"n": "ورق الحوض", "w": L+(2*H)+4.5, "h": W+(2*H)+4.5, "t": "p"},
            {"n": "ورق الغلاف", "w": (2*L)+(2*H)+7, "h": W+5, "t": "p"},
            {"n": "البطانة الداخلية", "w": (2*L)+(2*H), "h": W, "t": "p"}
        ]
    return []

# 4. الواجهة الرئيسية
c1, c2, c3 = st.columns([2, 1, 2])
with c2:
    if os.path.exists("logo.png"): st.image("logo.png")
    else: st.header("ULBE LOGO")

st.title("📊 حاسبة الإنتاج وتوفير الورق")

col_in1, col_in2 = st.columns(2)
with col_in1:
    box_type = st.selectbox("نوع الموديل", ["علبة وقبغ (قطعتين)", "علبة مغناطيسية", "علبة شريط (Kurdele)"])
    qty = st.number_input("الكمية", value=1000, step=100)
with col_in2:
    L = st.number_input("الطول الصافي (L)", value=20.0)
    W = st.number_input("العرض الصافي (W)", value=15.0)
    H = st.number_input("الارتفاع (H)", value=5.0)

# 5. منطق الحساب والذكاء الصناعي للتوفير
if st.button("تحليل التكلفة واقتراحات التوفير 🚀"):
    parts = get_box_structure(L, W, H, box_type)
    total_material_cost = 0
    
    st.subheader("🛠️ تحليل أجزاء العلبة")
    display_cols = st.columns(len(parts))
    
    for i, pt in enumerate(parts):
        # 1. الحساب الحالي
        current_per = max((70//pt['w'])*(100//pt['h']), (100//pt['w'])*(70//pt['h']))
        
        # 2. فحص التقليل الذكي (من 1سم إلى 3سم)
        best_save_msg = ""
        max_pieces = current_per
        
        if current_per > 0:
            for delta in [1.0, 2.0, 3.0]:
                # نجرب نقلل من الطول أو العرض الصافي (يؤثر على المفتوح)
                test_w, test_h = pt['w'] - delta, pt['h'] - delta
                test_per = max((70//test_w)*(100//test_h), (100//test_w)*(70//test_h))
                
                if test_per > max_pieces:
                    max_pieces = test_per
                    best_save_msg = f"💡 نصيحة: إذا قللت القياس بمقدار ({delta} سم)، ستحصل على {int(test_per)} قطعة بدلاً من {int(current_per)} في الطبقة!"

        # عرض التنبيه إذا وجد توفير
        if best_save_msg:
            st.markdown(f"<div class='tip-box'><b>{pt['n']}:</b> {best_save_msg}</div>", unsafe_allow_html=True)

        if current_per <= 0:
            st.error(f"❌ {pt['n']} قياسه شاذ!")
            continue

        sheets = math.ceil(qty / current_per)
        # أسعار افتراضية (تقدر تغيرها من السايد بار)
        price_per_sheet = 1200 if pt['t'] == 'b' else 250
        total_material_cost += (sheets * price_per_sheet)
        
        with display_cols[i]:
            st.metric(pt['n'], f"{int(current_per)} قطعة", f"{pt['w']}x{pt['h']} سم", delta_color="normal")

    # 6. النتائج المالية
    fixed_fees = 250000 # قوالب + عمال + طبع (تقريبي)
    grand_total = total_material_cost + fixed_fees
    if box_type == "علبة شريط (Kurdele)": grand_total += (qty * 200) # سعر الشريط
    
    st.divider()
    res_c1, res_c2 = st.columns(2)
    with res_c1:
        st.markdown(f"""
        <div class="result-card">
            <h3 style='margin:0; color:#1A1A1A !important;'>سعر العلبة المفرد</h3>
            <h1 style='color:#2E7D32 !important;'>{round(grand_total/qty)} دينار</h1>
        </div>
        """, unsafe_allow_html=True)
    with res_c2:
        st.markdown(f"""
        <div class="result-card">
            <h3 style='margin:0; color:#1A1A1A !important;'>إجمالي الفاتورة</h3>
            <h1 style='color:#2E7D32 !important;'>{format(int(grand_total), ',')} د.ع</h1>
        </div>
        """, unsafe_allow_html=True)

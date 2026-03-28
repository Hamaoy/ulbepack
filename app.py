import streamlit as st
import math
import os

# 1. إعدادات المظهر (Off-White & Clear Black Text)
st.set_page_config(page_title="ULBE Production Pro", layout="wide")

st.markdown("""
    <style>
    .stApp { background-color: #FDFCF8; color: #1A1A1A; }
    p, span, label, .stMarkdown, .stMetric { color: #1A1A1A !important; font-weight: 600; }
    h1, h2, h3, h4 { color: #004E96 !important; }
    .stNumberInput input, .stSelectbox div[data-baseweb="select"], .stRadio div { background-color: #FFFFFF !important; color: #000000 !important; }
    .result-card { background-color: #FFFFFF; padding: 20px; border-radius: 12px; border: 2px solid #004E96; box-shadow: 0 4px 10px rgba(0,0,0,0.1); margin-top:15px; }
    .tip-box { background-color: #E3F2FD; border-right: 6px solid #2196F3; padding: 12px; color: #0D47A1 !important; margin: 8px 0; border-radius: 4px; font-size: 14px; }
    .combine-box { background-color: #E8F5E9; border-right: 6px solid #4CAF50; padding: 12px; color: #1B5E20 !important; margin: 8px 0; border-radius: 4px; font-size: 14px; }
    .stButton>button { background-color: #004E96; color: white; font-weight: bold; height: 3.5em; width: 100%; border-radius:8px; }
    .sidebar-section { padding: 10px; background: #f0f0f0; border-radius: 8px; margin-bottom: 15px; }
    </style>
    """, unsafe_allow_html=True)

# 2. حماية النظام
if "auth" not in st.session_state: st.session_state.auth = False
if not st.session_state.auth:
    st.title("🔐 دخول النظام")
    if st.text_input("كلمة السر", type="password") == "ULBE2026":
        if st.button("دخول"): st.session_state.auth = True; st.rerun()
    st.stop()

# 3. إدارة الأسعار (Sidebar Fix)
if 'p' not in st.session_state:
    st.session_state.p = {
        "p_b": 1200, "p_p": 250, "dig": 1500, "rib": 300, 
        "lab": 50000, "mold": 100000, "print": 40000, "lam": 60000, "cut": 130000
    }

with st.sidebar:
    st.header("⚙️ الأسعار والتكاليف")
    ps = st.session_state.p
    
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.write("📦 المواد الأولية")
    ps["p_b"] = st.number_input("سعر الكارتون (70x100)", value=ps["p_b"])
    ps["p_p"] = st.number_input("سعر الورق الأوفست (70x100)", value=ps["p_p"])
    ps["dig"] = st.number_input("سعر ورق الديجيتال (33x70)", value=ps["dig"])
    ps["rib"] = st.number_input("سعر متر الشريط (Kurdele)", value=ps["rib"])
    st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown("<div class='sidebar-section'>", unsafe_allow_html=True)
    st.write("🛠️ أجور العمل")
    ps["lab"] = st.number_input("أجور العمال", value=ps["lab"])
    ps["mold"] = st.number_input("تكلفة القالب", value=ps["mold"])
    ps["print"] = st.number_input("أجور الطبع (للوجبة)", value=ps["print"])
    ps["lam"] = st.number_input("أجور السلفنة", value=ps["lam"])
    ps["cut"] = st.number_input("أجور التقطيع (الداي كت)", value=ps["cut"])
    st.markdown("</div>", unsafe_allow_html=True)

# 4. محرك الحسابات الهندسية
def get_box_structure(L, W, H, b_type):
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
            {"n": "البطانة (Inner)", "w": (2*L)+(2*H), "h": W, "t": "p"}
        ]
    elif b_type == "علبة جرارة (مجر)":
        return [
            {"n": "كارتون المجر", "w": L+(2*H), "h": W+(2*H), "t": "b"},
            {"n": "كارتون الكفر الخارجي", "w": (2*W)+(2*H)+2, "h": L, "t": "b"},
            {"n": "ورق المجر", "w": L+(2*H)+4.5, "h": W+(2*H)+4.5, "t": "p"},
            {"n": "ورق الكفر الخارجي", "w": (2*W)+(2*H)+7, "h": L+4.5, "t": "p"}
        ]
    return []

# خوارزمية الدمج للحصول على أقل خسارة ورق
def calculate_best_fit(w1, h1, w2, h2, sheet_w, sheet_h, qty):
    # حساب القطع بشكل منفصل
    p1 = max((sheet_w//w1)*(sheet_h//h1), (sheet_h//w1)*(sheet_w//h1))
    p2 = max((sheet_w//w2)*(sheet_h//h2), (sheet_h//w2)*(sheet_w//h2))
    sep_sheets = (math.ceil(qty/p1) if p1>0 else float('inf')) + (math.ceil(qty/p2) if p2>0 else float('inf'))
    
    # حساب القطع إذا دمجناهم بقطعة واحدة (جنب بعض أو فوق بعض)
    W_side, H_side = w1 + w2, max(h1, h2)
    p_comb1 = max((sheet_w//W_side)*(sheet_h//H_side), (sheet_h//W_side)*(sheet_w//H_side))
    
    W_top, H_top = max(w1, w2), h1 + h2
    p_comb2 = max((sheet_w//W_top)*(sheet_h//H_top), (sheet_h//W_top)*(sheet_w//H_top))
    
    best_comb = max(p_comb1, p_comb2)
    comb_sheets = math.ceil(qty/best_comb) if best_comb > 0 else float('inf')
    
    if comb_sheets < sep_sheets:
        return True, comb_sheets, best_comb  # الدمج أفضل
    return False, sep_sheets, (p1, p2) # المنفصل أفضل

# 5. الواجهة الرئيسية
c1, c2, c3 = st.columns([2, 1, 2])
with c2:
    if os.path.exists("logo.png"): st.image("logo.png")

st.title("📊 نظام ULBE الشامل للتسعير")

col_in1, col_in2 = st.columns(2)
with col_in1:
    box_type = st.selectbox("نوع الموديل", ["علبة وقبغ (قطعتين)", "علبة مغناطيسية", "علبة شريط (Kurdele)", "علبة جرارة (مجر)"])
    print_method = st.radio("طريقة الطباعة (للورق)", ["أوفست (70x100)", "ديجيتال (33x70)"], horizontal=True)
    qty = st.number_input("الكمية", value=1000, step=100)
with col_in2:
    L = st.number_input("الطول الصافي (L)", value=20.0)
    W = st.number_input("العرض الصافي (W)", value=15.0)
    H = st.number_input("الارتفاع (H)", value=5.0)

# 6. الحسابات
if st.button("احسب الفاتورة وحلل الإنتاج 🚀"):
    parts = get_box_structure(L, W, H, box_type)
    
    board_parts = [p for p in parts if p['t'] == 'b']
    paper_parts = [p for p in parts if p['t'] == 'p']
    
    total_board_sheets = 0
    total_paper_sheets = 0
    
    st.subheader("🛠️ تحليل استهلاك المواد")
    
    # --- معالجة الكارتون (مع الدمج) ---
    if len(board_parts) >= 2:
        is_comb, sheets, data = calculate_best_fit(board_parts[0]['w'], board_parts[0]['h'], board_parts[1]['w'], board_parts[1]['h'], 70, 100, qty)
        if is_comb:
            total_board_sheets += sheets
            st.markdown(f"<div class='combine-box'>✅ <b>توفير ذكي:</b> تم دمج ({board_parts[0]['n']}) و ({board_parts[1]['n']}) في نفس لوح الكارتون، ستحصل على {data} سيت كامل باللوح الواحد!</div>", unsafe_allow_html=True)
        else:
            for pt in board_parts:
                per = max((70//pt['w'])*(100//pt['h']), (100//pt['w'])*(70//pt['h']))
                total_board_sheets += math.ceil(qty / per) if per > 0 else 0
                st.write(f"- {pt['n']}: {int(per)} قطعة باللوح.")
    
    # --- معالجة الورق (مع الدمج حسب طريقة الطباعة) ---
    paper_w, paper_h = (33, 70) if "ديجيتال" in print_method else (70, 100)
    if len(paper_parts) >= 2:
        is_comb, sheets, data = calculate_best_fit(paper_parts[0]['w'], paper_parts[0]['h'], paper_parts[1]['w'], paper_parts[1]['h'], paper_w, paper_h, qty)
        if is_comb:
            total_paper_sheets += sheets
            st.markdown(f"<div class='combine-box'>✅ <b>توفير ذكي:</b> تم دمج أوراق ({paper_parts[0]['n']}) و ({paper_parts[1]['n']}) في نفس فرخ الورق ({paper_w}x{paper_h}). ستحصل على {data} سيت بالفرخ!</div>", unsafe_allow_html=True)
        else:
            for pt in paper_parts:
                per = max((paper_w//pt['w'])*(paper_h//pt['h']), (paper_h//pt['w'])*(paper_w//pt['h']))
                total_paper_sheets += math.ceil(qty / per) if per > 0 else 0
                st.write(f"- {pt['n']}: {int(per)} قطعة بالفرخ ({paper_w}x{paper_h}).")
    
    # معالجة أي قطع إضافية (مثل البطانة بالمغناطيسية)
    if len(paper_parts) > 2:
        for pt in paper_parts[2:]:
            per = max((paper_w//pt['w'])*(paper_h//pt['h']), (paper_h//pt['w'])*(paper_w//pt['h']))
            total_paper_sheets += math.ceil(qty / per) if per > 0 else 0
            st.write(f"- {pt['n']}: {int(per)} قطعة بالفرخ.")

    # --- نصائح التوفير (3 سم) ---
    st.markdown("#### 💡 نصائح تقليل القياس (الرادار)")
    for pt in parts:
        sheet_w, sheet_h = 70, 100
        if pt['t'] == 'p' and "ديجيتال" in print_method: sheet_w, sheet_h = 33, 70
        curr_per = max((sheet_w//pt['w'])*(sheet_h//pt['h']), (sheet_h//pt['w'])*(sheet_w//pt['h']))
        
        if curr_per > 0:
            for delta in [1.0, 2.0, 3.0]:
                test_per = max((sheet_w//(pt['w']-delta))*(sheet_h//(pt['h']-delta)), (sheet_h//(pt['w']-delta))*(sheet_w//(pt['h']-delta)))
                if test_per > curr_per:
                    st.markdown(f"<div class='tip-box'><b>{pt['n']}:</b> تصغير القياس {delta} سم يزيد القطع من {int(curr_per)} إلى {int(test_per)}!</div>", unsafe_allow_html=True)
                    break # نعرض أفضل نصيحة فقط للقطعة

    # --- الحسابات المالية ---
    cost_board = total_board_sheets * ps['p_b']
    paper_price = ps['dig'] if "ديجيتال" in print_method else ps['p_p']
    cost_paper = total_paper_sheets * paper_price
    
    ribbon_cost = (qty * 0.6 * ps['rib']) if box_type == "علبة شريط (Kurdele)" else 0
    work_costs = ps['mold'] + ps['lab'] + ps['print'] + ps['lam'] + ps['cut']
    grand_total = cost_board + cost_paper + ribbon_cost + work_costs

    # --- الفاتورة التفصيلية بالكتابة ---
    st.divider()
    st.markdown(f"""
    <div class="result-card">
        <h2 style='text-align:center; color:#2E7D32 !important;'>الفاتورة التفصيلية للطلب</h2>
        <table style='width:100%; font-size:18px; line-height:2;'>
            <tr>
                <td><b>الكارتون:</b></td>
                <td style='text-align:left;'>{int(total_board_sheets)} لوح × {ps['p_b']} دينار = <b>{format(int(cost_board), ',')} دينار</b></td>
            </tr>
            <tr>
                <td><b>الورق ({print_method}):</b></td>
                <td style='text-align:left;'>{int(total_paper_sheets)} فرخ × {paper_price} دينار = <b>{format(int(cost_paper), ',')} دينار</b></td>
            </tr>
            {"<tr><td><b>الشريط:</b></td><td style='text-align:left;'>"+str(qty)+" علبة × "+str(ps['rib'])+" دينار/متر = <b>"+format(int(ribbon_cost), ',')+" دينار</b></td></tr>" if ribbon_cost > 0 else ""}
            <tr>
                <td><b>أجور العمل والتشغيل (قالب، طبع، سلفنة..):</b></td>
                <td style='text-align:left;'><b>{format(int(work_costs), ',')} دينار</b></td>
            </tr>
            <tr style='background-color:#E8F5E9; font-size:24px; color:#1B5E20;'>
                <td><b>الإجمالي الكلي:</b></td>
                <td style='text-align:left;'><b>{format(int(grand_total), ',')} دينار</b></td>
            </tr>
            <tr style='font-size:20px; color:#004E96;'>
                <td><b>سعر العلبة المفردة:</b></td>
                <td style='text-align:left;'><b>{round(grand_total/qty)} دينار</b></td>
            </tr>
        </table>
    </div>
    """, unsafe_allow_html=True)

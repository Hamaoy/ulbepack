import streamlit as st
import math
import os

# 1. إعداد الواجهة
st.set_page_config(page_title="Rigid Box Calculator", layout="wide")

# 2. نظام الحماية
PASSWORD = "ULBE2026"

def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center;'>🔐 Sistem Kilitli / النظام مغلق</h2>", unsafe_allow_html=True)
        pwd = st.text_input("Password / كلمة المرور", type="password")
        if st.button("Giriş / دخول"):
            if pwd == PASSWORD:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ Hatalı Şifre / كلمة مرور خاطئة")
        return False
    return True

if not check_password():
    st.stop()

# 3. نظام اللغات (قاموس الكلمات)
languages = {
    "Arabic": {
        "title": "نظام التسعير الذكي للكرتون المقوى",
        "settings": "🛠️ إعدادات التكاليف",
        "board_price": "سعر طبقة الكارتون (70x100)",
        "paper_price": "سعر طبقة الورق (70x100)",
        "sets_label": "🎨 أجور الوجبة (لحد 1300)",
        "print_cost": "أجور الطبع",
        "lam_cost": "أجور السلفنة",
        "cut_labor": "أجور التقطيع",
        "fixed_label": "🏗️ القوالب والنقل",
        "die_cost": "قالب التقطيع",
        "zinc_cost": "قالب الزنك",
        "trans_cost": "النقليات",
        "mag_price": "سعر زوج المغناطيس",
        "order_details": "📦 الطلبية",
        "box_type": "نوع الععلبة",
        "qty": "العدد المطلوب",
        "add_mag": "إضافة مغناطيس؟",
        "dims": "📐 القياسات (سم)",
        "length": "الطول", "width": "العرض", "height": "الارتفاع",
        "calc_btn": "🚀 احسب الآن",
        "unit_price": "سعر الععلبة الواحدة",
        "total_price": "الإجمالي الكلي",
        "tech_rep": "📑 التقرير الفني",
        "breakdown": "تفاصيل التكاليف",
        "saving_tip": "💡 نصيحة: تقليل الطول {i} ملم يزيد الإنتاج لـ {res} قطع."
    },
    "Turkish": {
        "title": "Akıllı Sert Kutu Fiyatlandırma Sistemi",
        "settings": "🛠️ Maliyet Ayarları",
        "board_price": "Mukavva Plaka Fiyatı (70x100)",
        "paper_price": "Kağıt Plaka Fiyatı (70x100)",
        "sets_label": "🎨 İşlem Ücretleri (1300 adede kadar)",
        "print_cost": "Baskı Ücreti",
        "lam_cost": "Selefon Ücreti",
        "cut_labor": "Kesim İşçiliği",
        "fixed_label": "🏗️ Kalıplar ve Nakliye",
        "die_cost": "Kesim Kalıbı",
        "zinc_cost": "Baskı Kalıbı (Zinko)",
        "trans_cost": "Nakliye",
        "mag_price": "Mıknatıs Çifti Fiyatı",
        "order_details": "📦 Sipariş Detayları",
        "box_type": "Kutu Tipi",
        "qty": "Sipariş Adedi",
        "add_mag": "Mıknatıs Eklensin mi?",
        "dims": "📐 Ölçüler (cm)",
        "length": "Boy", "width": "En", "height": "Yükseklik",
        "calc_btn": "🚀 Hesapla",
        "unit_price": "Birim Kutu Fiyatı",
        "total_price": "Toplam Tutar",
        "tech_rep": "📑 Teknik Rapor",
        "breakdown": "Maliyet Detayları",
        "saving_tip": "💡 İpucu: Boyu {i} mm azaltırsanız, tabaka başına üretim {res} adede çıkar."
    }
}

# اختيار اللغة
lang_choice = st.selectbox("🌐 Choose Language / اختر اللغة", ["Arabic", "Turkish"])
ln = languages[lang_choice]

# 4. التصميم
st.markdown(f"""
    <style>
    .stApp {{ background-color: #0e1117; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }}
    h1 {{ text-align: center; font-size: 24px !important; border-bottom: 1px solid #30363d; padding-bottom: 10px; }}
    [data-testid="stMetricValue"] {{ color: #00ff41 !important; }}
    .stButton>button {{ width: 100%; background-color: #238636; color: white; font-weight: bold; border: none; height: 3em; }}
    #MainMenu, footer {{visibility: hidden;}}
    </style>
    """, unsafe_allow_html=True)

if os.path.exists("logo.png"):
    st.image("logo.png", width=120)

st.title(ln["title"])

# 5. الإعدادات الجانبية
with st.sidebar:
    st.markdown(f"### {ln['settings']}")
    p_b = st.number_input(ln["board_price"], value=1200)
    p_p = st.number_input(ln["paper_price"], value=235)
    st.divider()
    st.markdown(f"### {ln['sets_label']}")
    s_p = st.number_input(ln["print_cost"], value=40000)
    s_l = st.number_input(ln["lam_cost"], value=60000)
    s_c = st.number_input(ln["cut_labor"], value=130000)
    st.divider()
    st.markdown(f"### {ln['fixed_label']}")
    c_d = st.number_input(ln["die_cost"], value=100000)
    c_z = st.number_input(ln["zinc_cost"], value=30000)
    c_t = st.number_input(ln["trans_cost"], value=25000)
    st.divider()
    m_p = st.number_input(ln["mag_price"], value=500)

# 6. الإدخال الرئيسي
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"### {ln['order_details']}")
    b_t = st.selectbox(ln["box_type"], ["Top & Bottom", "Magnetic", "Drawer"] if lang_choice=="Turkish" else ["علبة وقبغ (قطعتين)", "علبة مغناطيسية", "علبة جرارة"])
    q = st.number_input(ln["qty"], value=1000, step=100)
    u_m = st.checkbox(ln["add_mag"])

with col2:
    st.markdown(f"### {ln['dims']}")
    lc, wc, hc = st.columns(3)
    L = lc.number_input(ln["length"], value=26.0)
    W = wc.number_input(ln["width"], value=17.0)
    H = hc.number_input(ln["height"], value=4.0)

if st.button(ln["calc_btn"]):
    # الحسابات (نفس المنطق السابق)
    extra = 6 if b_t in ["علبة وقبغ (قطعتين)", "Top & Bottom"] else 9
    bw, bh = L + (H * 2), W + (H * 2)
    pw, ph = bw + extra, bh + extra
    b_per = (70 // bw) * (100 // bh)
    p_full = ((50 // pw) * (70 // ph)) * 2
    
    if b_per > 0 and p_full > 0:
        total_b = math.ceil(q / b_per)
        total_p = math.ceil(q / p_full)
        sets = math.ceil((total_p * 2) / 1300)
        
        m_cost = (total_b * p_b) + (total_p * p_p)
        w_cost = (sets * (s_p + s_l + s_c))
        f_cost = c_d + c_z + c_t + (q * m_p if u_m else 0)
        total = m_cost + w_cost + f_cost
        
        c1, c2 = st.columns(2)
        c1.metric(ln["unit_price"], f"{round(total/q)} IQD")
        c2.metric(ln["total_price"], f"{format(total, ',')} IQD")
        
        st.markdown(f"### {ln['tech_rep']}")
        st.write(f"- Mukavva/كارتون: {total_b} | Kağıt/ورق: {total_p} | Sets/وجبات: {sets}")

import streamlit as st
import math
import os

# 1. إعداد الواجهة
st.set_page_config(page_title="نظام تسعير الورشة | Rigid Box Calculator", layout="wide")

# 2. نظام الحماية (كلمة المرور)
PASSWORD = "ULBE2026"

def check_password():
    if "password_correct" not in st.session_state:
        st.markdown("<h2 style='text-align: center; color: white;'>🔐 النظام مغلق / Sistem Kilitli</h2>", unsafe_allow_html=True)
        pwd = st.text_input("كلمة المرور / Şifre", type="password")
        if st.button("دخول / Giriş"):
            if pwd == PASSWORD:
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("❌ كلمة مرور خاطئة / Hatalı Şifre")
        return False
    return True

if not check_password():
    st.stop()

# 3. قاموس اللغات الشامل
langs = {
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
        "box_type": "نوع العلبة",
        "b_types": ["علبة وقبغ (قطعتين)", "علبة مغناطيسية", "علبة جرارة"],
        "qty": "العدد المطلوب",
        "add_mag": "إضافة مغناطيس؟",
        "dims": "📐 القياسات (سم)",
        "L": "الطول", "W": "العرض", "H": "الارتفاع",
        "calc_btn": "🚀 احسب التكلفة التفصيلية",
        "unit_price": "سعر العلبة الواحدة",
        "total_price": "الإجمالي الكلي",
        "rep_title": "📑 تقرير المطبعة التفصيلي",
        "mat_title": "📦 المواد والكميات",
        "mat_b": "طبقات الكارتون (70x100):",
        "mat_p": "طبقات الورق (70x100):",
        "mat_per": "العلب بالطبقة الواحدة:",
        "tech_title": "🛠️ العمليات الفنية",
        "tech_p": "أوراق الطبع (50x70):",
        "tech_sets": "عدد الوجبات (Sets):",
        "tech_cost": "أجور العمليات:",
        "tbl_item": "البند", "tbl_cost": "التكلفة (دينار)",
        "tbl_m": "المواد الخام", "tbl_o": "أجور العمليات", "tbl_f": "القوالب والثوابت",
        "sugg_title": "💡 المستشار الذكي (مقترحات التوفير)",
        "sugg_ok": "✅ القياسات الحالية مثالية وتستغل مساحة الكارتون بأفضل شكل.",
        "sugg_msg": "إذا قللت **{dim}** بمقدار **{val} ملم**، سيرتفع الإنتاج إلى **{res} علب** بالطبقة، وستوفر مبالغ كبيرة!"
    },
    "Turkish": {
        "title": "Akıllı Sert Kutu Fiyatlandırma Sistemi",
        "settings": "🛠️ Maliyet Ayarları",
        "board_price": "Mukavva Plaka Fiyatı (70x100)",
        "paper_price": "Kağıt Plaka Fiyatı (70x100)",
        "sets_label": "🎨 İşlem Ücretleri (1300'e kadar)",
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
        "b_types": ["Alt & Üst Kutu", "Mıknatıslı Kutu", "Çekmeceli Kutu"],
        "qty": "Sipariş Adedi",
        "add_mag": "Mıknatıs Eklensin mi?",
        "dims": "📐 Ölçüler (cm)",
        "L": "Boy", "W": "En", "H": "Yükseklik",
        "calc_btn": "🚀 Detaylı Hesapla",
        "unit_price": "Birim Kutu Fiyatı",
        "total_price": "Toplam Tutar",
        "rep_title": "📑 Detaylı Üretim Raporu",
        "mat_title": "📦 Malzemeler ve Miktarlar",
        "mat_b": "Mukavva Plaka (70x100):",
        "mat_p": "Kağıt Plaka (70x100):",
        "mat_per": "Plaka Başına Kutu:",
        "tech_title": "🛠️ Teknik İşlemler",
        "tech_p": "Baskı Kağıdı (50x70):",
        "tech_sets": "Hesaplanan Set (Vardiya):",
        "tech_cost": "İşlem Ücretleri:",
        "tbl_item": "Kalem", "tbl_cost": "Maliyet (IQD)",
        "tbl_m": "Ham Madde", "tbl_o": "İşçilik ve İşlem", "tbl_f": "Kalıp ve Sabitler",
        "sugg_title": "💡 Akıllı Tasarruf Önerisi",
        "sugg_ok": "✅ Mevcut ölçüler plaka alanını mükemmel kullanıyor.",
        "sugg_msg": "**{dim}** ölçüsünü **{val} mm** azaltırsanız, üretim plakada **{res} adede** çıkar ve büyük tasarruf sağlarsınız!"
    }
}

# اختيار اللغة
lang_choice = st.selectbox("🌐 لغة النظام / Sistem Dili", ["Arabic", "Turkish"])
ln = langs[lang_choice]

# 4. التصميم وتجميل الواجهة
st.markdown("""
    <style>
    .stApp { background-color: #0e1117; color: #e0e0e0; font-family: 'Segoe UI', sans-serif; }
    h1 { text-align: center; font-size: 26px !important; border-bottom: 1px solid #30363d; padding-bottom: 10px; color: #ffffff;}
    [data-testid="stMetricValue"] { color: #00ff41 !important; font-size: 32px !important; }
    [data-testid="stMetricLabel"] { font-size: 16px !important; color: #8b949e !important; }
    .stButton>button { width: 100%; background-color: #238636; color: white; font-weight: bold; height: 3.5em; border-radius: 8px; border: none; font-size: 18px;}
    .stButton>button:hover { background-color: #2ea043; }
    .stAlert { background-color: #161b22; border: 1px solid #d29922; border-radius: 8px; }
    .stTable { background-color: #161b22; border-radius: 8px; }
    #MainMenu, footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)

if os.path.exists("logo.png"):
    st.markdown('<div style="display:flex; justify-content:center; margin-bottom:15px;"><img src="logo.png" width="130" style="border-radius:10px;"></div>', unsafe_allow_html=True)

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

# 6. واجهة إدخال الطلب
col1, col2 = st.columns(2)
with col1:
    st.markdown(f"### {ln['order_details']}")
    b_t = st.selectbox(ln["box_type"], ln["b_types"])
    q = st.number_input(ln["qty"], value=1000, step=100)
    u_m = st.checkbox(ln["add_mag"])

with col2:
    st.markdown(f"### {ln['dims']}")
    lc, wc, hc = st.columns(3)
    L = lc.number_input(ln["L"], value=26.0)
    W = wc.number_input(ln["W"], value=17.0)
    H = hc.number_input(ln["H"], value=4.0)

# 7. محرك الحسابات (منفصل حتى نستخدمه بالاستشارة الذكية)
def engine(l, w, h, b_type):
    # تحديد الزيادة بناءً على فهرس الاختيار حتى يشتغل باللغتين
    idx = ln["b_types"].index(b_type)
    extra = 6 if idx == 0 else 9 
    
    bw, bh = l + (h * 2), w + (h * 2)
    pw, ph = bw + extra, bh + extra
    
    b_per = (70 // bw) * (100 // bh)
    p_full = ((50 // pw) * (70 // ph)) * 2
    return b_per, p_full

st.markdown("<br>", unsafe_allow_html=True)

if st.button(ln["calc_btn"]):
    b_per, p_full = engine(L, W, H, b_t)
    
    if b_per > 0 and p_full > 0:
        total_b = math.ceil(q / b_per)
        total_p = math.ceil(q / p_full)
        pr_50x70 = total_p * 2
        sets = math.ceil(pr_50x70 / 1300)
        
        m_cost = (total_b * p_b) + (total_p * p_p)
        w_cost = (sets * (s_p + s_l + s_c))
        f_cost = c_d + c_z + c_t + (q * m_p if u_m else 0)
        total = m_cost + w_cost + f_cost
        
        # --- الأسعار الأساسية ---
        c1, c2 = st.columns(2)
        c1.metric(ln["unit_price"], f"{round(total/q)} IQD")
        c2.metric(ln["total_price"], f"{format(total, ',')} IQD")
        
        st.divider()
        
        # --- التقرير التفصيلي (الذي طلبته) ---
        st.markdown(f"### {ln['rep_title']}")
        r_col1, r_col2 = st.columns(2)
        with r_col1:
            st.info(f"""
            **{ln['mat_title']}**
            - {ln['mat_b']} **{total_b}**
            - {ln['mat_p']} **{total_p}**
            - {ln['mat_per']} **{b_per}**
            """)
        with r_col2:
            st.info(f"""
            **{ln['tech_title']}**
            - {ln['tech_p']} **{pr_50x70}**
            - {ln['tech_sets']} **{sets}**
            - {ln['tech_cost']} **{format(w_cost, ',')}** IQD
            """)

        # جدول التكاليف
        st.table({
            ln["tbl_item"]: [ln["tbl_m"], ln["tbl_o"], ln["tbl_f"]],
            ln["tbl_cost"]: [format(m_cost, ','), format(w_cost, ','), format(f_cost, ',')]
        })

        # --- المستشار الذكي (يفحص الطول والعرض) ---
        st.markdown(f"### {ln['sugg_title']}")
        found_better = False
        
        # 1. فحص الطول
        for i in range(1, 11):
            test_b, _ = engine(L - (i*0.1), W, H, b_t)
            if test_b > b_per:
                st.warning(ln["sugg_msg"].format(dim=ln["L"], val=i, res=test_b))
                found_better = True
                break # نكتفي بأول توفير نلقاه للطول
                
        # 2. فحص العرض
        for i in range(1, 11):
            test_b, _ = engine(L, W - (i*0.1), H, b_t)
            if test_b > b_per:
                st.warning(ln["sugg_msg"].format(dim=ln["W"], val=i, res=test_b))
                found_better = True
                break

        if not found_better:
            st.success(ln["sugg_ok"])
    else:
        st.error("القياسات المدخلة أكبر من حجم الطبقة المسموح به! / Girilen ölçüler plaka boyutundan büyük!")

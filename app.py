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

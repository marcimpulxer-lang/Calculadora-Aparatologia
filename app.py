import streamlit as st
import pandas as pd
from PIL import Image
from fpdf import FPDF
import io
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
st.set_page_config(page_title="Calculadora ROI Impulxer", layout="wide")

brand_color = "#996600"

st.markdown(f"""
    <style>
    .main {{ background-color: #f8f9fa; }}
    .main-title {{ font-size: 2.2rem; font-weight: bold; margin-bottom: 1rem; }}
    @media (max-width: 768px) {{
        .main-title {{ font-size: 1.5rem !important; }}
        .stImage img {{ width: 150px !important; }}
    }}
    .stProgress > div > div > div > div {{ background-color: {brand_color}; }}
    div[data-testid="stMetricValue"] {{ color: {brand_color}; }}
    .footer {{
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #ffffff; color: #555555; text-align: center;
        padding: 15px; font-size: 0.8rem; border-top: 1px solid #e0e0e0; z-index: 1000;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. LOGO
logo_path = 'Logo Academia-black (1).png'
try:
    image = Image.open(logo_path)
    st.image(image, width=220)
except:
    logo_path = None

st.markdown('<p class="main-title">📊 Simulador de Rentabilidad de Aparatología</p>', unsafe_allow_html=True)

# 3. BARRA LATERAL
with st.sidebar:
    st.header("🖊️ Identificación del Equipo")
    nombre_aparato = st.text_input("Nombre del Aparato", value="Láser Diodo")
    marca_aparato = st.text_input("Marca / Modelo", value="Impulxer Pro")
    st.markdown("---")
    st.header("📋 Datos de la Inversión")
    inv_sin_iva = st.number_input("Inversión Equipo (sin IVA)", value=15000.0)
    iva_pct = st.slider("IVA %", 0, 21, 21)
    costes_adic = st.number_input("Otros costes", value=300.0)
    intereses = st.number_input("Intereses", value=2000.0)
    st.header("⏱️ Capacidad")
    anos_amort = st.slider("Años de amortización", 1, 10, 5)
    semanas_ano = st.slider("Semanas laborales/año", 1, 52, 48)
    sesiones_sem_max = st.number_input("Capacidad máx. (ses/sem)", value=30)
    st.header("💰 Estrategia")
    precio_sesion = st.number_input("Precio venta sesión (€)", value=60.0)
    sesiones_reales_mes = st.slider("Sesiones reales al mes", 1, 100, 6)

# 4. CÁLCULOS
inv_total_iva = (inv_sin_iva * (1 + iva_pct/100)) + costes_adic + intereses
coste_mensual = (inv_total_iva / anos_amort) / 12
beneficio_mensual_real = (sesiones_reales_mes * precio_sesion) - coste_mensual

# 5. DASHBOARD
st.subheader(f"Análisis: {nombre_aparato} ({marca_aparato})")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Inversión Total", f"{inv_total_iva:,.2f} €")
col2.metric("Coste Mensual", f"{coste_mensual:,.2f} €")
col3.metric("Beneficio Mes", f"{beneficio_mensual_real:,.2f} €")
col4.metric("¿Rentable?", "✅ SÍ" if beneficio_mensual_real > 0 else "❌ NO")

# 6. FUNCIÓN DE GENERACIÓN DE PDF CORREGIDA
def create_pdf_bytes():
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    
    # Header
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INFORME DE RENTABILIDAD - IMPULXER", ln=True, align="C")
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 10, f"Generado el: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="R")
    pdf.ln(10)
    
    # Bloque Datos
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, " 1. IDENTIFICACION DEL EQUIPO", ln=True, fill=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f" Aparato: {nombre_aparato}", ln=True)
    pdf.cell(0, 8, f" Marca/Modelo: {marca_aparato}", ln=True)
    pdf.ln(5)
    
    # Bloque Financiero
    pdf.set_font("Arial", "B", 12)
    pdf.cell(0, 10, " 2. ANALISIS FINANCIERO MENSUAL", ln=True, fill=True)
    pdf.set_font("Arial", "", 11)
    pdf.cell(0, 8, f" Inversion Total (con IVA e intereses): {inv_total_iva:,.2f} EUR", ln=True)
    pdf.cell(0, 8, f" Coste Fijo Mensual (Amortizacion): {coste_mensual:,.2f} EUR", ln=True)
    pdf.cell(0, 8, f" Precio por Sesion: {precio_sesion:,.2f} EUR", ln=True)
    pdf.cell(0, 8, f" Sesiones Reales/Mes: {sesiones_reales_mes}", ln=True)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 8, f" BENEFICIO NETO MENSUAL: {beneficio_mensual_real:,.2f} EUR", ln=True)
    pdf.ln(15)
    
    # Disclaimer
    pdf.set_font("Arial", "I", 8)
    disclaimer = ("Este informe es una simulacion orientativa basada en los datos introducidos por el usuario. "
                  "Impulxer Academy SL no se hace responsable de discrepancias con la realidad. "
                  "Propiedad de Impulxer Academy SL - 2026")
    pdf.multi_cell(0, 5, disclaimer)
    
    # Convertir a bytes para Streamlit
    return pdf.output()

st.markdown("---")
st.subheader("📥 Exportar Resultados")
col_pdf, _ = st.columns([1, 2])

with col_pdf:
    # Generamos el contenido del PDF
    pdf_output = create_pdf_bytes()
    
    # Botón de descarga con los datos ya en formato correcto
    st.download_button(
        label="💾 Descargar Informe PDF",
        data=bytes(pdf_output), # Forzamos la conversión a bytes
        file_name=f"ROI_{nombre_aparato.replace(' ','_')}.pdf",
        mime="application/pdf"
    )

# 7. FOOTER
st.markdown(f"""<div class="footer">Este simulador es orientativo. Impulxer Academy no se hace responsable de discrepancias.<br><strong>Propiedad de Impulxer Academy SL - 2026</strong></div>""", unsafe_allow_html=True)

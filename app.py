import streamlit as st
import pandas as pd
from PIL import Image
from fpdf import FPDF
import io
import os
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
    .stProgress > div > div > div > div {{ background-color: {brand_color} !important; }}
    div[data-testid="stMetricValue"] {{ color: {brand_color}; }}
    button[aria-selected="true"] {{ border-bottom-color: {brand_color} !important; color: {brand_color} !important; }}
    button[aria-selected="true"] p {{ color: {brand_color} !important; }}
    .footer {{
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #ffffff; color: #555555; text-align: center;
        padding: 15px; font-size: 0.8rem; border-top: 1px solid #e0e0e0; z-index: 1000;
    }}
    .spacer {{ height: 100px; }}
    </style>
    """, unsafe_allow_html=True)

# 2. LOGO
logo_filename = 'Logo Academia-black (1).png'
try:
    image = Image.open(logo_filename)
    st.image(image, width=220)
    logo_exists = True
except:
    logo_exists = False

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
    intereses = st.number_input("Intereses financiación", value=2000.0)
    st.header("⏱️ Capacidad de Trabajo")
    anos_amort = st.slider("Años de amortización", 1, 10, 5)
    semanas_ano = st.slider("Semanas laborales/año", 1, 52, 48)
    sesiones_sem_max = st.number_input("Capacidad máx. (sesiones/sem)", value=30)
    st.header("💰 Estrategia de Precios")
    precio_sesion = st.number_input("Precio venta sesión (€)", value=60.0)
    sesiones_reales_mes = st.slider("Sesiones reales al mes", 1, 100, 6)

# 4. CÁLCULOS
inv_total_iva = (inv_sin_iva * (1 + iva_pct/100)) + costes_adic + intereses
coste_mensual = (inv_total_iva / anos_amort) / 12
total_ses_teoricas = anos_amort * semanas_ano * sesiones_sem_max
coste_unitario_sesion = inv_total_iva / total_ses_teoricas if total_ses_teoricas > 0 else 0
beneficio_mensual_real = (sesiones_reales_mes * precio_sesion) - coste_mensual
punto_equilibrio = coste_mensual / precio_sesion if precio_sesion > 0 else 0

# 5. DASHBOARD
st.subheader(f"Análisis: {nombre_aparato} ({marca_aparato})")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Inversión Total", f"{inv_total_iva:,.2f} €")
col2.metric("Coste Mensual", f"{coste_mensual:,.2f} €")
col3.metric("Beneficio Mes", f"{beneficio_mensual_real:,.2f} €")
col4.metric("¿Rentable?", "✅ SÍ" if beneficio_mensual_real > 0 else "❌ NO")

st.markdown("---")

tab1, tab2 = st.tabs(["🔍 Análisis Detallado", "📈 Escenarios de Crecimiento"])
with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.write(f"**Coste por sesión:** {coste_unitario_sesion:.2f} €")
        st.write(f"**Punto de equilibrio:** {punto_equilibrio:.2f} sesiones/mes")
    with c2:
        margen_pct = ((precio_sesion - coste_unitario_sesion) / precio_sesion * 100) if precio_sesion > 0 else 0
        st.write(f"**Margen Bruto:** {margen_pct:.2f}%")
        st.progress(min(max(margen_pct/100, 0.0), 1.0))

with tab2:
    escenarios = [5, 10, 20, 30, 40, 50]
    data_esc = [[s, f"{s*precio_sesion:,.2f} €", f"{(s*precio_sesion)-coste_mensual:,.2f} €"] for s in escenarios]
    st.table(pd.DataFrame(data_esc, columns=["Sesiones/Mes", "Ingresos", "Neto Mensual"]))

# 6. FUNCIÓN PDF MEJORADA (Logo + Tabla)
def create_pdf_bytes():
    pdf = FPDF()
    pdf.add_page()
    
    # Logo corregido
    if logo_exists:
        pdf.image(logo_filename, x=10, y=8, w=35)
    
    pdf.set_font("Arial", "B", 16)
    pdf.ln(10)
    pdf.cell(0, 10, "INFORME DE RENTABILIDAD", ln=True, align="C")
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="R")
    pdf.ln(10)
    
    # Sección Equipo
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, f" EQUIPO: {nombre_aparato} / {marca_aparato}", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f" Inversion Total: {inv_total_iva:,.2f} EUR", ln=True)
    pdf.cell(0, 7, f" Amortizacion Mensual: {coste_mensual:,.2f} EUR", ln=True)
    pdf.cell(0, 7, f" Precio Venta Sesion: {precio_sesion:,.2f} EUR", ln=True)
    pdf.ln(5)
    
    # Tabla de Escenarios en PDF
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, " PROYECCION DE ESCENARIOS", ln=True, fill=True)
    pdf.set_font("Arial", "B", 10)
    pdf.cell(40, 8, " Sesiones/Mes", 1)
    pdf.cell(60, 8, " Ingresos", 1)
    pdf.cell(60, 8, " Beneficio Neto", 1, ln=True)
    
    pdf.set_font("Arial", "", 10)
    for s in escenarios:
        pdf.cell(40, 8, f" {s}", 1)
        pdf.cell(60, 8, f" {s*precio_sesion:,.2f} EUR", 1)
        pdf.cell(60, 8, f" {(s*precio_sesion)-coste_mensual:,.2f} EUR", 1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    disclaimer = "Este informe es una simulacion orientativa basada en los datos introducidos por el usuario. Impulxer Academy SL no se hace responsable de discrepancias con la realidad. Propiedad de Impulxer Academy SL - 2026"
    pdf.multi_cell(0, 5, disclaimer)
    
    return pdf.output()

st.markdown("---")
st.subheader("📥 Exportar Informe")
st.download_button(
    label="💾 Descargar PDF Oficial",
    data=bytes(create_pdf_bytes()),
    file_name=f"ROI_{nombre_aparato}.pdf",
    mime="application/pdf"
)

st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
st.markdown(f"""<div class="footer">Simulador orientativo. Impulxer Academy no se hace responsable de discrepancias.<br><strong>Propiedad de Impulxer Academy SL - 2026</strong></div>""", unsafe_allow_html=True)

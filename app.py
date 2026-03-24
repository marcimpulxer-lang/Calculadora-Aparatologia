import streamlit as st
import pandas as pd
from PIL import Image
from fpdf import FPDF
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

# 3. BARRA LATERAL (ENTRADAS)
with st.sidebar:
    st.header("🖊️ Identificación del Equipo")
    nombre_aparato = st.text_input("Nombre del Aparato", value="Láser Diodo")
    marca_aparato = st.text_input("Marca / Modelo", value="Impulxer Pro")
    st.markdown("---")
    st.header("📋 Datos de la Inversión")
    inv_sin_iva = st.number_input("Inversión Equipo (sin IVA)", value=15000.0)
    iva_pct = st.slider("IVA %", 0, 21, 21)
    costes_adic = st.number_input("Formación y otros costes", value=300.0)
    intereses = st.number_input("Intereses financiación", value=2000.0)
    st.header("⏱️ Capacidad de Trabajo")
    anos_amort = st.slider("Años de amortización", 1, 10, 5)
    semanas_ano = st.slider("Semanas laborales/año", 1, 52, 48)
    sesiones_sem_max = st.number_input("Capacidad máx. (sesiones/sem)", value=30)
    minutos_sesion = st.number_input("Duración media sesión (min)", value=60)
    st.header("💰 Estrategia de Precios")
    precio_sesion = st.number_input("Precio venta sesión (€)", value=60.0)
    sesiones_reales_mes = st.slider("Sesiones reales al mes", 1, 100, 6)

# 4. CÁLCULOS MAESTROS (Réplica exacta del archivo original)
inv_total_iva = (inv_sin_iva * (1 + iva_pct/100)) + costes_adic + intereses
coste_anual_amort = inv_total_iva / anos_amort
coste_mensual_fijo = coste_anual_amort / 12

# Capacidad y eficiencia
total_sesiones_teoricas_anuales = semanas_ano * sesiones_sem_max
# Coste por sesión basado en la capacidad de amortización (Celda F24 original)
coste_unitario_sesion = inv_total_iva / (total_sesiones_teoricas_anuales * anos_amort) if (total_sesiones_teoricas_anuales * anos_amort) > 0 else 0
coste_minuto = coste_unitario_sesion / minutos_sesion if minutos_sesion > 0 else 0

# Resultados Reales
beneficio_por_sesion = precio_sesion - coste_unitario_sesion
margen_bruto_pct = (beneficio_por_sesion / precio_sesion * 100) if precio_sesion > 0 else 0
beneficio_mensual_real = (sesiones_reales_mes * precio_sesion) - coste_mensual_fijo
ingresos_anuales_est = (sesiones_reales_mes * precio_sesion) * 12
punto_equilibrio_mes = coste_mensual_fijo / precio_sesion if precio_sesion > 0 else 0
ocupacion_real_pct = (sesiones_reales_mes / (sesiones_sem_max * 4)) * 100 if (sesiones_sem_max > 0) else 0

# 5. DASHBOARD PRINCIPAL
st.subheader(f"Análisis: {nombre_aparato} ({marca_aparato})")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Inversión Total", f"{inv_total_iva:,.2f} €")
col2.metric("Coste Mensual Fijo", f"{coste_mensual_fijo:,.2f} €")
col3.metric("Beneficio Mes", f"{beneficio_mensual_real:,.2f} €")
col4.metric("¿Rentable?", "✅ SÍ" if beneficio_mensual_real > 0 else "❌ NO")

st.markdown("---")

# 6. PESTAÑAS CON TODOS LOS CONCEPTOS ORIGINALES
tab1, tab2 = st.tabs(["🔍 Análisis Detallado", "📈 Escenarios de Crecimiento"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Amortización y Costes")
        st.write(f"**Coste por sesión (amortización):** {coste_unitario_sesion:.2f} €")
        st.write(f"**Coste por minuto de uso:** {coste_minuto:.4f} €")
        st.write(f"**Sesiones/mes para Punto de Equilibrio:** {punto_equilibrio_mes:.2f}")
        st.write(f"**Ingresos anuales estimados:** {ingresos_anuales_est:,.2f} €")
    with c2:
        st.subheader("Márgenes y Ocupación")
        st.write(f"**Beneficio por sesión:** {beneficio_por_sesion:.2f} €")
        st.write(f"**Margen Bruto sobre precio:** {margen_bruto_pct:.2f}%")
        st.write(f"**% Ocupación Real:** {ocupacion_real_pct:.1f}%")
        st.progress(min(max(margen_bruto_pct/100, 0.0), 1.0))

with tab2:
    st.subheader("Comparativa de Escenarios")
    escenarios = [5, 10, 20, 30, 40, 50, 60]
    data_esc = []
    for s in escenarios:
        ing = s * precio_sesion
        ben = ing - coste_mensual_fijo
        ocup = (s / (sesiones_sem_max * 4)) * 100 if (sesiones_sem_max > 0) else 0
        data_esc.append([s, f"{ing:,.2f} €", f"{ben:,.2f} €", "Sí" if ben > 0 else "No", f"{ocup:.1f}%"])
    
    st.table(pd.DataFrame(data_esc, columns=["Sesiones/Mes", "Ingresos", "Neto Mensual", "Rentable", "% Ocupación"]))

# 7. FUNCIÓN PDF COMPLETA
def create_pdf_bytes():
    pdf = FPDF()
    pdf.add_page()
    if logo_exists:
        pdf.image(logo_filename, x=10, y=8, w=35)
    pdf.set_font("Arial", "B", 16)
    pdf.ln(10)
    pdf.cell(0, 10, "INFORME DE RENTABILIDAD DETALLADO", ln=True, align="C")
    pdf.set_font("Arial", "", 9)
    pdf.cell(0, 5, f"Generado: {datetime.now().strftime('%d/%m/%Y %H:%M')}", ln=True, align="R")
    pdf.ln(10)
    
    pdf.set_fill_color(240, 240, 240)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, f" 1. IDENTIFICACION Y CAPACIDAD", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f" Equipo: {nombre_aparato} ({marca_aparato})", ln=True)
    pdf.cell(0, 7, f" Capacidad Maxima: {sesiones_sem_max} sesiones/semana", ln=True)
    pdf.cell(0, 7, f" Tiempo por sesion: {minutos_sesion} minutos", ln=True)
    pdf.ln(3)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, " 2. ANALISIS DE COSTES Y MARGENES", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f" Inversion Total: {inv_total_iva:,.2f} EUR", ln=True)
    pdf.cell(0, 7, f" Coste Mensual Amortizacion: {coste_mensual_fijo:,.2f} EUR", ln=True)
    pdf.cell(0, 7, f" Coste Real por Sesion: {coste_unitario_sesion:.2f} EUR", ln=True)
    pdf.cell(0, 7, f" Coste por Minuto: {coste_minuto:.4f} EUR", ln=True)
    pdf.cell(0, 7, f" Beneficio por Sesion: {beneficio_por_sesion:.2f} EUR", ln=True)
    pdf.cell(0, 7, f" Margen Bruto: {margen_bruto_pct:.2f}%", ln=True)
    pdf.ln(3)

    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, " 3. PROYECCION DE ESCENARIOS", ln=True, fill=True)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(30, 8, " Ses/Mes", 1)
    pdf.cell(50, 8, " Ingresos", 1)
    pdf.cell(50, 8, " Beneficio Neto", 1)
    pdf.cell(30, 8, " % Ocupacion", 1, ln=True)
    pdf.set_font("Arial", "", 9)
    for s in escenarios:
        pdf.cell(30, 7, f" {s}", 1)
        pdf.cell(50, 7, f" {s*precio_sesion:,.2f} EUR", 1)
        pdf.cell(50, 7, f" {(s*precio_sesion)-coste_mensual_fijo:,.2f} EUR", 1)
        pdf.cell(30, 7, f" {(s/(sesiones_sem_max*4))*100:.1f}%", 1, ln=True)
    
    pdf.ln(10)
    pdf.set_font("Arial", "I", 8)
    disclaimer = "Este informe es una simulacion orientativa. Impulxer Academy SL no se hace responsable de discrepancias con la realidad. Propiedad de Impulxer Academy SL - 2026"
    pdf.multi_cell(0, 5, disclaimer)
    return pdf.output()

st.markdown("---")
st.subheader("📥 Exportar Informe Completo")
st.download_button(
    label="💾 Descargar PDF Oficial",
    data=bytes(create_pdf_bytes()),
    file_name=f"ROI_{nombre_aparato.replace(' ','_')}.pdf",
    mime="application/pdf"
)

st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
st.markdown(f"""<div class="footer">Este simulador es solo orientativo. Impulxer Academy no se hace responsable de discrepancias con la realidad.<br><strong>Propiedad de Impulxer Academy SL - 2026</strong></div>""", unsafe_allow_html=True)

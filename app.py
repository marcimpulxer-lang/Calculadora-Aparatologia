import streamlit as st
import pandas as pd
from PIL import Image
from fpdf import FPDF
from datetime import datetime

# 1. CONFIGURACIÓN Y ESTILO
st.set_page_config(page_title="Calculadora ROI Impulxer", layout="wide")
brand_color = "#996600"

st.markdown(f"""
    <style>
    .main {{ background-color: #f8f9fa; }}
    .main-title {{ font-size: 2.2rem; font-weight: bold; margin-bottom: 1rem; color: #333; }}
    @media (max-width: 768px) {{
        .main-title {{ font-size: 1.5rem !important; }}
        .stImage img {{ width: 140px !important; }}
    }}
    .stProgress > div > div > div > div {{ background-color: {brand_color} !important; }}
    div[data-testid="stMetricValue"] {{ color: {brand_color}; }}
    button[aria-selected="true"] {{ border-bottom-color: {brand_color} !important; color: {brand_color} !important; }}
    button[aria-selected="true"] p {{ color: {brand_color} !important; }}
    .cta-container {{
        background-color: #ffffff; padding: 25px; border-radius: 12px;
        border: 2px solid {brand_color}; text-align: center; margin-top: 10px;
    }}
    .vsl-button {{
        display: inline-block; padding: 14px 20px; background-color: {brand_color};
        color: white !important; text-decoration: none; border-radius: 6px;
        font-weight: bold; width: 100%; transition: 0.3s;
    }}
    .vsl-button:hover {{ background-color: #7a5200; transform: translateY(-2px); }}
    .footer {{
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #ffffff; color: #555; text-align: center;
        padding: 12px; font-size: 0.8rem; border-top: 1px solid #eee; z-index: 1000;
    }}
    .spacer {{ height: 120px; }}
    </style>
    """, unsafe_allow_html=True)

# 2. CARGA DE LOGO
logo_filename = 'Logo Academia-black (1).png'
try:
    image = Image.open(logo_filename)
    st.image(image, width=200)
    logo_exists = True
except:
    logo_exists = False

st.markdown('<p class="main-title">📊 Simulador de Rentabilidad de Aparatología</p>', unsafe_allow_html=True)

# 3. ENTRADAS LATERALES
with st.sidebar:
    st.header("🖊️ Identificación")
    nombre_aparato = st.text_input("Nombre del Aparato", placeholder="Ej: Láser Diodo")
    marca_aparato = st.text_input("Marca / Modelo", placeholder="Ej: Impulxer Pro")
    st.markdown("---")
    st.header("📋 Inversión")
    inv_sin_iva = st.number_input("Inversión (sin IVA)", value=0.0)
    iva_pct = st.slider("IVA %", 0, 21, 21)
    costes_adic = st.number_input("Otros costes", value=0.0)
    intereses = st.number_input("Intereses", value=0.0)
    st.header("⏱️ Capacidad")
    anos_amort = st.slider("Años amortización", 1, 10, 5)
    semanas_ano = st.slider("Semanas/año", 1, 52, 48)
    ses_sem_max = st.number_input("Capacidad máx (ses/sem)", value=0)
    min_sesion = st.number_input("Minutos/sesión", value=0)
    st.header("💰 Venta")
    precio_sesion = st.number_input("Precio sesión (€)", value=0.0)
    ses_reales_mes = st.slider("Sesiones reales/mes", 0, 120, 0)

# 4. LÓGICA DE CÁLCULO
inv_total = (inv_sin_iva * (1 + iva_pct/100)) + costes_adic + intereses
c_mensual_fijo = (inv_total / anos_amort) / 12 if anos_amort > 0 else 0
vida_util_ses = anos_amort * semanas_ano * ses_sem_max
c_sesion = inv_total / vida_util_ses if vida_util_ses > 0 else 0
c_minuto = c_sesion / min_sesion if min_sesion > 0 else 0
ben_sesion = precio_sesion - c_sesion
margen_pct = (ben_sesion / precio_sesion * 100) if precio_sesion > 0 else 0
ben_mensual = (ses_reales_mes * precio_sesion) - c_mensual_fijo
ing_anuales = (ses_reales_mes * precio_sesion) * 12
ocup_pct = (ses_reales_mes / (ses_sem_max * 4.33)) * 100 if ses_sem_max > 0 else 0

# 5. UI PRINCIPAL
st.subheader(f"Análisis: {nombre_aparato if nombre_aparato else 'Nuevo Equipo'}")
col1, col2, col3, col4 = st.columns(4)
col1.metric("Inversión Total", f"{inv_total:,.2f} €")
col2.metric("Coste Fijo Mes", f"{c_mensual_fijo:,.2f} €")
col3.metric("Beneficio Mes", f"{ben_mensual:,.2f} €")
col4.metric("¿Rentable?", "✅ SÍ" if ben_mensual > 0 else "❌ NO")

t1, t2 = st.tabs(["🔍 Análisis Detallado", "📈 Escenarios"])
with t1:
    ca, cb = st.columns(2)
    with ca:
        st.write(f"**Coste por sesión:** {c_sesion:.2f} €")
        st.write(f"**Coste por minuto:** {c_minuto:.4f} €")
        st.write(f"**Ingresos anuales (est):** {ing_anuales:,.0f} €")
    with cb:
        st.write(f"**Beneficio por sesión:** {ben_sesion:.2f} €")
        st.write(f"**Margen Bruto:** {margen_pct:.1f}%")
        st.write(f"**% Ocupación Real:** {ocup_pct:.1f}%")
        st.progress(min(max(margen_pct/100, 0.0), 1.0))

with t2:
    esc = [5, 10, 20, 30, 50, 80]
    data_esc = [[s, f"{s*precio_sesion:,.0f} €", f"{(s*precio_sesion)-c_mensual_fijo:,.0f} €", f"{(s/(ses_sem_max*4.33 if ses_sem_max>0 else 1))*100:.1f}%"] for s in esc]
    st.table(pd.DataFrame(data_esc, columns=["Ses/Mes", "Ingresos", "Neto", "% Ocupación"]))

# 6. PDF Y CTA
def create_pdf():
    pdf = FPDF(); pdf.add_page()
    if logo_exists: pdf.image(logo_filename, x=10, y=8, w=35)
    pdf.set_font("Arial", "B", 16); pdf.ln(10); pdf.cell(0, 10, "INFORME ROI - IMPULXER", ln=True, align="C")
    pdf.set_font("Arial", "", 10); pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="R"); pdf.ln(10)
    pdf.set_fill_color(240, 240, 240); pdf.set_font("Arial", "B", 11); pdf.cell(0, 10, f" EQUIPO: {nombre_aparato}", ln=True, fill=True)
    pdf.set_font("Arial", "", 10); pdf.cell(0, 7, f" Inv. Total: {inv_total:,.2f} EUR | Neto Mes: {ben_mensual:,.2f} EUR", ln=True); pdf.ln(5)
    pdf.set_font("Arial", "B", 11); pdf.cell(0, 10, " PROYECCION DE ESCENARIOS", ln=True, fill=True)
    for s in esc:
        pdf.cell(0, 7, f" Sesiones: {s} | Ingresos: {s*precio_sesion:,.0f} EUR | Neto: {(s*precio_sesion)-c_mensual_fijo:,.0f} EUR", ln=True)
    pdf.ln(10); pdf.set_font("Arial", "I", 8); pdf.multi_cell(0, 5, "Simulacion orientativa. Propiedad de Impulxer Academy SL - 2026")
    return pdf.output()

st.markdown("---")
c_p, c_c = st.columns(2)
with c_p:
    st.download_button("💾 Descargar PDF Oficial", data=bytes(create_pdf()), file_name="ROI_Impulxer.pdf", mime="application/pdf")
with c_c:
    st.markdown(f'<div class="cta-container"><p style="font-weight:bold;">¿Te ha gustado?</p><a href="https://impulxer.com/vsl-abril26/" target="_blank" class="vsl-button">Haz click aquí y mira más</a></div>', unsafe_allow_html=True)

st.markdown('<div class="spacer"></div><div class="footer">Simulador orientativo. Impulxer Academy SL - 2026</div>', unsafe_allow_html=True)

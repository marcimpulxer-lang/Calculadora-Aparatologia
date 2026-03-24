import streamlit as st
import pandas as pd
from PIL import Image
from fpdf import FPDF
from datetime import datetime

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
st.set_page_config(page_title="Calculadora ROI Aparotología - Impulxer", layout="wide")
brand_color = "#996600"

st.markdown(f"""
    <style>
    .main {{ background-color: #f8f9fa; }}
    .main-title {{ font-size: 2.2rem; font-weight: bold; margin-bottom: 1rem; color: #333; }}
    
    /* Responsive */
    @media (max-width: 768px) {{
        .main-title {{ font-size: 1.5rem !important; }}
        .stImage img {{ width: 140px !important; }}
    }}

    /* Estilos de Marca */
    .stProgress > div > div > div > div {{ background-color: {brand_color} !important; }}
    div[data-testid="stMetricValue"] {{ color: {brand_color}; }}
    button[aria-selected="true"] {{ border-bottom-color: {brand_color} !important; color: {brand_color} !important; }}
    button[aria-selected="true"] p {{ color: {brand_color} !important; }}

    /* CTA Especial */
    .cta-container {{
        background-color: #ffffff;
        padding: 25px;
        border-radius: 12px;
        border: 2px solid {brand_color};
        text-align: center;
        margin-top: 10px;
    }}
    .vsl-button {{
        display: inline-block;
        padding: 14px 20px;
        background-color: {brand_color};
        color: white !important;
        text-decoration: none;
        border-radius: 6px;
        font-weight: bold;
        width: 100%;
        transition: 0.3s;
    }}
    .vsl-button:hover {{ background-color: #7a5200; transform: translateY(-2px); }}

    /* Footer */
    .footer {{
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #ffffff; color: #555; text-align: center;
        padding: 12px; font-size: 0.8rem; border-top: 1px solid #eee; z-index: 1000;
    }}
    .spacer {{ height: 120px; }}
    </style>
    """, unsafe_allow_html=True)

# 2. LOGO
logo_filename = 'Logo Academia-black (1).png'
try:
    image = Image.open(logo_filename)
    st.image(image, width=200)
    logo_exists = True
except:
    logo_exists = False

st.markdown('<p class="main-title">📊 Simulador de Rentabilidad de Aparatología</p>', unsafe_allow_html=True)

# 3. BARRA LATERAL (ENTRADAS)
with st.sidebar:
    st.header("🖊️ Identificación del Equipo")
    nombre_aparato = st.text_input("Nombre del Aparato", value="ej: Láser Diodo")
    marca_aparato = st.text_input("Marca / Modelo", value="Ej: Impulxer Pro")
    st.markdown("---")
    st.header("📋 Datos de la Inversión")
    inv_sin_iva = st.number_input("Inversión Equipo (sin IVA)", value=0.0, step=0.0)
    iva_pct = st.slider("IVA %", 0, 21, 21)
    costes_adic = st.number_input("Formación y otros costes", value=0.0)
    intereses = st.number_input("Intereses financiación", value=0.0)
    st.header("⏱️ Capacidad de Trabajo")
    anos_amort = st.slider("Años de amortización", 1, 10, 5)
    semanas_ano = st.slider("Semanas laborales/año", 1, 52, 48)
    sesiones_sem_max = st.number_input("Capacidad máx. (sesiones/sem)", value=0)
    minutos_sesion = st.number_input("Minutos por sesión", value=0)
    st.header("💰 Estrategia de Precios")
    precio_sesion = st.number_input("Precio venta sesión (€)", value=0.0)
    sesiones_reales_mes = st.slider("Sesiones reales al mes", 1, 100, 6)

# 4. CÁLCULOS MAESTROS (Revisados vs Original)
inv_total_iva = (inv_sin_iva * (1 + iva_pct/100)) + costes_adic + intereses
coste_mensual_fijo = (inv_total_iva / anos_amort) / 12
total_ses_teoricas_vida = anos_amort * semanas_ano * sesiones_sem_max
coste_unitario_sesion = inv_total_iva / total_ses_teoricas_vida if total_ses_teoricas_vida > 0 else 0
coste_minuto = coste_unitario_sesion / minutos_sesion if minutos_sesion > 0 else 0
beneficio_sesion = precio_sesion - coste_unitario_sesion
margen_bruto_pct = (beneficio_sesion / precio_sesion * 100) if precio_sesion > 0 else 0
beneficio_mensual_real = (sesiones_reales_mes * precio_sesion) - coste_mensual_fijo
ingresos_anuales_est = (sesiones_reales_mes * precio_sesion) * 12
punto_equilibrio_mes = coste_mensual_fijo / precio_sesion if precio_sesion > 0 else 0
ocupacion_real_pct = (sesiones_reales_mes / (sesiones_sem_max * 4.33)) * 100 if sesiones_sem_max > 0 else 0

# 5. DASHBOARD PRINCIPAL
st.subheader(f"Análisis: {nombre_aparato} | {marca_aparato}")
c1, c2, c3, c4 = st.columns(4)
c1.metric("Inversión Total", f"{inv_total_iva:,.2f} €")
c2.metric("Coste Fijo Mes", f"{coste_mensual_fijo:,.2f} €")
c3.metric("Beneficio Mes", f"{beneficio_mensual_real:,.2f} €")
c4.metric("¿Es Rentable?", "✅ SÍ" if beneficio_mensual_real > 0 else "❌ NO")

st.markdown("---")

# 6. PESTAÑAS (ANALISIS + ESCENARIOS)
t_an, t_es = st.tabs(["🔍 Análisis Detallado", "📈 Escenarios de Crecimiento"])

with t_an:
    col_a, col_b = st.columns(2)
    with col_a:
        st.subheader("Eficiencia y Tiempos")
        st.write(f"**Coste por sesión:** {coste_unitario_sesion:.2f} €")
        st.write(f"**Coste por minuto:** {coste_minuto:.4f} €")
        st.write(f"**Punto equilibrio (ses/mes):** {punto_equilibrio_mes:.2f}")
        st.write(f"**Ingresos anuales (est):** {ingresos_anuales_est:,.0f} €")
    with col_b:
        st.subheader("Rendimiento Real")
        st.write(f"**Beneficio por sesión:** {beneficio_sesion:.2f} €")
        st.write(f"**Margen Bruto:** {margen_bruto_pct:.1f}%")
        st.write(f"**% Ocupación Real:** {ocupacion_real_pct:.1f}%")
        st.progress(min(max(margen_bruto_pct/100, 0.0), 1.0))

with t_es:
    st.subheader("Proyección de Escenarios")
    vol_esc = [5, 10, 20, 30, 40, 50, 60]
    df_esc = []
    for s in vol_esc:
        ben = (s * precio_sesion) - coste_mensual_fijo
        ocp = (s / (sesiones_sem_max * 4.33)) * 100 if sesiones_sem_max > 0 else 0
        df_esc.append([s, f"{s*precio_sesion:,.0f} €", f"{ben:,.0f} €", "Sí" if ben > 0 else "No", f"{ocp:.1f}%"])
    st.table(pd.DataFrame(df_esc, columns=["Ses/Mes", "Ingresos", "Neto", "Rentable", "% Ocupación"]))

# 7. EXPORTACIÓN Y CTA
def get_pdf():
    pdf = FPDF(); pdf.add_page()
    if logo_exists: pdf.image(logo_filename, x=10, y=8, w=35)
    pdf.set_font("Arial", "B", 16); pdf.ln(10)
    pdf.cell(0, 10, "INFORME DE RENTABILIDAD DETALLADO", ln=True, align="C")
    pdf.set_font("Arial", "", 9); pdf.cell(0, 5, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="R"); pdf.ln(10)
    pdf.set_fill_color(240, 240, 240); pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, f" 1. DATOS DEL EQUIPO: {nombre_aparato} ({marca_aparato})", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f" Inversion Total: {inv_total_iva:,.2f} EUR | Coste Mensual: {coste_mensual_fijo:,.2f} EUR", ln=True)
    pdf.cell(0, 7, f" Coste Sesion: {coste_unitario_sesion:.2f} EUR | Coste Minuto: {coste_minuto:.4f} EUR", ln=True)
    pdf.ln(5); pdf.set_font("Arial", "B", 11); pdf.cell(0, 10, " 2. TABLA DE ESCENARIOS", ln=True, fill=True)
    pdf.set_font("Arial", "B", 9); pdf.cell(30, 8, " Ses/Mes", 1); pdf.cell(50, 8, " Ingresos", 1); pdf.cell(50, 8, " Beneficio", 1); pdf.cell(30, 8, " % Ocupacion", 1, ln=True)
    pdf.set_font("Arial", "", 9)
    for s in vol_esc:
        pdf.cell(30, 7, f" {s}", 1); pdf.cell(50, 7, f" {s*precio_sesion:,.0f} EUR", 1); pdf.cell(50, 7, f" {(s*precio_sesion)-coste_mensual_fijo:,.0f} EUR", 1); pdf.cell(30, 7, f" {(s/(sesiones_sem_max*4.33))*100:.1f}%", 1, ln=True)
    pdf.ln(10); pdf.set_font("Arial", "I", 8); pdf.multi_cell(0, 5, "Disclaimer: Simulacion orientativa. Impulxer Academy SL - 2026")
    return pdf.output()

st.markdown("---")
c_d, c_c = st.columns(2)
with c_d:
    st.subheader("📥 Informe")
    st.download_button(label="💾 Descargar PDF Oficial", data=bytes(get_pdf()), file_name=f"ROI_{nombre_aparato}.pdf", mime="application/pdf")
with c_c:
    st.subheader("🚀 Próximo Paso")
    st.markdown(f'<div class="cta-container"><p style="font-weight:bold; margin-bottom:10px;">¿Te ha gustado esta herramienta?</p><a href="https://impulxer.com/vsl-abril26/" target="_blank" class="vsl-button">Click aquí y mira qué más ofrecemos</a></div>', unsafe_allow_html=True)

st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
st.markdown(f'<div class="footer">Este simulador es solo orientativo. Impulxer Academy no se hace responsable de discrepancias reales.<br><strong>Propiedad de Impulxer Academy SL - 2026</strong></div>', unsafe_allow_html=True)

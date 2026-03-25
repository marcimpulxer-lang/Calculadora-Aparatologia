import streamlit as st
import pandas as pd
from PIL import Image
from fpdf import FPDF
from datetime import datetime

# 1. CONFIGURACIÓN Y ESTILOS (Mantenidos exactamente igual)
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
        border: 2px solid {brand_color}; text-align: center; margin-top: 20px;
    }}
    .vsl-button {{
        display: inline-block; padding: 16px 24px; background-color: {brand_color};
        color: white !important; text-decoration: none; border-radius: 8px;
        font-weight: bold; width: 100%; transition: 0.3s;
    }}
    .footer {{
        position: fixed; left: 0; bottom: 0; width: 100%;
        background-color: #ffffff; color: #555; text-align: center;
        padding: 15px; font-size: 0.8rem; border-top: 1px solid #e0e0e0; z-index: 1000;
    }}
    .spacer {{ height: 130px; }}
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

# 3. BARRA LATERAL (Campos descriptivos recuperados)
with st.sidebar:
    st.header("🖊️ Identifica tu simulación")
    nombre_aparato = st.text_input("Nombre del aparato", placeholder="Ej: Láser de Diodo")
    marca_aparato = st.text_input("Marca/modelo", placeholder="Ej: Impulxer Pro")
    
    st.markdown("---")
    st.header("📋 En inversión")
    inv_sin_iva = st.number_input("Coste de la máquina (Sin IVA)", value=0.0, step=500.0)
    iva_pct = st.slider("IVA", 0, 21, 21)
    costes_adic = st.number_input("Otros costes asociados (Producto, Transporte, formación...)", value=0.0)
    intereses = st.number_input("Intereses finales (Solo si es financiado)", value=0.0)
    
    st.header("⏱️ Capacidad de Amortización")
    anos_amort = st.slider("Años de amortización o de crédito", 1, 10, 5)
    semanas_ano = st.slider("Semanas del año laborales previstas", 1, 52, 48)
    sesiones_sem_prev = st.number_input("Nº de sesiones por semana previstas", value=0)
    minutos_sesion = st.number_input("Minutos estimados por sesión", value=0)

    st.header("💰 En Venta del tratamiento")
    coste_hora_centro = st.number_input("Coste general por hora del centro", value=0.0)
    precio_sesion = st.number_input("Precio por sesión y tratamiento", value=0.0)

# 4. CÁLCULOS MAESTROS
inv_total_iva = (inv_sin_iva * (1 + iva_pct/100)) + costes_adic + intereses
coste_mensual_fijo = (inv_total_iva / anos_amort) / 12 if anos_amort > 0 else 0
total_ses_teoricas_anuales = semanas_ano * sesiones_sem_prev
coste_amort_sesion = inv_total_iva / (total_ses_teoricas_anuales * anos_amort) if (total_ses_teoricas_anuales * anos_amort) > 0 else 0
coste_centro_minuto = coste_hora_centro / 60 if coste_hora_centro > 0 else 0
coste_total_sesion = coste_amort_sesion + (coste_centro_minuto * minutos_sesion)

# 5. DASHBOARD PRINCIPAL
st.subheader(f"Simulación: {nombre_aparato if nombre_aparato else 'Nuevo Equipo'}")
c1, c2, c3 = st.columns(3)
c1.metric("Inversión Total", f"{inv_total_iva:,.2f} €")
c2.metric("Coste Mensual de Amortización", f"{coste_mensual_fijo:,.2f} €")
c3.metric("Coste Real por Sesión", f"{coste_total_sesion:,.2f} €")

st.markdown("---")

# 6. PESTAÑAS (Analítica Detallada con Sliders)
tab1, tab2 = st.tabs(["🔍 Analítica Detallada", "📈 Escenarios de Crecimiento"])

with tab1:
    sesiones_reales_mes = st.slider("Nº de Sesiones reales que realizarás al mes", 0, 200, 0)
    
    beneficio_sesion = precio_sesion - coste_total_sesion
    beneficio_mensual = (sesiones_reales_mes * precio_sesion) - coste_mensual_fijo - (sesiones_reales_mes * coste_centro_minuto * minutos_sesion)
    ing_anuales = (sesiones_reales_mes * precio_sesion) * 12
    margen_pct = (beneficio_sesion / precio_sesion * 100) if precio_sesion > 0 else 0
    punto_equilibrio = coste_mensual_fijo / (precio_sesion - (coste_centro_minuto * minutos_sesion)) if (precio_sesion - (coste_centro_minuto * minutos_sesion)) > 0 else 0
    
    ca, cb, cc = st.columns(3)
    ca.metric("Beneficio Mensual Neto", f"{beneficio_mensual:,.2f} €")
    cb.metric("Margen Bruto", f"{margen_pct:.1f}%")
    cc.metric("¿Es Rentable?", "✅ SÍ" if beneficio_mensual > 0 else "❌ NO")
    
    st.markdown("---")
    col_inf1, col_inf2 = st.columns(2)
    with col_inf1:
        st.write(f"**Coste de amortización por sesión:** {coste_amort_sesion:.2f} €")
        st.write(f"**Coste de tiempo de centro por sesión:** {coste_centro_minuto * minutos_sesion:.2f} €")
        st.write(f"**Coste por minuto de tratamiento:** {coste_total_sesion / minutos_sesion if minutos_sesion > 0 else 0:.4f} €")
    with col_inf2:
        st.write(f"**Punto de equilibrio (sesiones/mes):** {punto_equilibrio:.2f}")
        st.write(f"**Beneficio neto por sesión:** {beneficio_sesion:.2f} €")
        st.write(f"**Ingresos anuales estimados:** {ing_anuales:,.2f} €")

with tab2:
    st.subheader("Comparativa de Escenarios")
    vol_esc = [5, 10, 20, 30, 40, 50, 75, 100]
    df_esc = []
    for s in vol_esc:
        ben = (s * precio_sesion) - coste_mensual_fijo - (s * coste_centro_minuto * minutos_sesion)
        df_esc.append([s, f"{s*precio_sesion:,.2f} €", f"{ben:,.2f} €", "Sí" if ben > 0 else "No"])
    st.table(pd.DataFrame(df_esc, columns=["Sesiones/Mes", "Ingresos Totales", "Beneficio Neto", "Rentable"]))

# 7. FUNCIÓN PDF AMPLIADA (Analítica Completa)
def create_pdf_bytes():
    pdf = FPDF(); pdf.add_page()
    if logo_exists: pdf.image(logo_filename, x=10, y=8, w=35)
    pdf.set_font("Arial", "B", 16); pdf.ln(10)
    pdf.cell(0, 10, "INFORME ANALITICO DE RENTABILIDAD PRO", ln=True, align="C")
    pdf.set_font("Arial", "", 9); pdf.cell(0, 5, f"Fecha: {datetime.now().strftime('%d/%m/%Y')}", ln=True, align="R"); pdf.ln(10)
    
    # 1. Configuración de Inversión
    pdf.set_fill_color(240, 240, 240); pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, " 1. DETALLES DE LA INVERSION", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f" Equipo: {nombre_aparato} | Marca: {marca_aparato}", ln=True)
    pdf.cell(0, 7, f" Inversion sin IVA: {inv_sin_iva:,.2f} EUR | IVA Aplicado: {iva_pct}%", ln=True)
    pdf.cell(0, 7, f" Otros costes (Transporte/Formacion): {costes_adic:,.2f} EUR | Intereses: {intereses:,.2f} EUR", ln=True)
    pdf.set_font("Arial", "B", 10); pdf.cell(0, 7, f" INVERSION TOTAL FINAL: {inv_total_iva:,.2f} EUR", ln=True)
    pdf.ln(3)

    # 2. Analítica Avanzada (LO QUE FALTABA)
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, " 2. ANALITICA AVANZADA Y MARGENES", ln=True, fill=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f" Amortizacion Mensual Fija: {coste_mensual_fijo:,.2f} EUR", ln=True)
    pdf.cell(0, 7, f" Coste Amortizacion por Sesion: {coste_amort_sesion:.2f} EUR", ln=True)
    pdf.cell(0, 7, f" Coste Centro por Sesion: {coste_centro_minuto * minutos_sesion:.2f} EUR", ln=True)
    pdf.set_font("Arial", "B", 10); pdf.cell(0, 7, f" COSTE REAL TOTAL POR SESION: {coste_total_sesion:.2f} EUR", ln=True)
    pdf.set_font("Arial", "", 10)
    pdf.cell(0, 7, f" Beneficio Neto por Sesion: {beneficio_sesion:.2f} EUR | Margen Bruto: {margen_pct:.1f}%", ln=True)
    pdf.cell(0, 7, f" Punto de Equilibrio Necesario: {punto_equilibrio:.2f} sesiones/mes", ln=True)
    pdf.cell(0, 7, f" Ingresos Anuales Proyectados: {ing_anuales:,.2f} EUR", ln=True)
    pdf.ln(3)

    # 3. Escenarios
    pdf.set_font("Arial", "B", 11)
    pdf.cell(0, 10, " 3. TABLA DE PROYECCION DE ESCENARIOS", ln=True, fill=True)
    pdf.set_font("Arial", "B", 9)
    pdf.cell(40, 8, " Sesiones/Mes", 1); pdf.cell(60, 8, " Ingresos Totales", 1); pdf.cell(60, 8, " Beneficio Neto", 1, ln=True)
    pdf.set_font("Arial", "", 9)
    for s in vol_esc:
        ben_esc = (s * precio_sesion) - coste_mensual_fijo - (s * coste_centro_minuto * minutos_sesion)
        pdf.cell(40, 7, f" {s}", 1); pdf.cell(60, 7, f" {s*precio_sesion:,.2f} EUR", 1); pdf.cell(60, 7, f" {ben_esc:,.2f} EUR", 1, ln=True)

    pdf.ln(10); pdf.set_font("Arial", "I", 8)
    pdf.multi_cell(0, 5, "Este simulador es solo orientativo. Impulxer Academy no se hace responsable de discrepancias con la realidad, es responsabilidad del usuario introducir los datos con la mayor exactitud para que el resultado sea lo más real posible. Propiedad de Impulxer Academy SL - 2026")
    return pdf.output()

# 8. CTA Y FOOTER (Exactamente iguales)
st.markdown("---")
c_p, c_c = st.columns(2)
with c_p:
    st.subheader("📥 Exportar Informe")
    st.download_button(label="💾 Descargar PDF con Analítica Avanzada", data=bytes(create_pdf_bytes()), file_name=f"Informe_ROI_{nombre_aparato}.pdf", mime="application/pdf")

with c_c:
    st.subheader("🚀 Próximo Paso")
    st.markdown(f"""
        <div class="cta-container">
            <p style="font-weight:bold; margin-bottom:15px;">¿Te ha gustado esta herramienta?</p>
            <a href="https://impulxer.com/vsl-abril26/" target="_blank" class="vsl-button">Hacer click aquí y mira qué más podemos ofrecerte</a>
        </div>
    """, unsafe_allow_html=True)

st.markdown('<div class="spacer"></div>', unsafe_allow_html=True)
st.markdown(f"""<div class="footer">Este simulador es solo orientativo. Impulxer Academy no se hace responsable de discrepancias con la realidad, es responsabilidad del usuario introducir los datos con la mayor exactitud para que el resultado sea lo más real posible. Propiedad de Impulxer Academy SL - 2026</div>""", unsafe_allow_html=True)

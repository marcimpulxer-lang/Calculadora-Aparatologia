import streamlit as st
import pandas as pd
from PIL import Image
import io

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS AVANZADOS (CSS)
st.set_page_config(page_title="Calculadora ROI Impulxer", layout="wide")

# Tu color corporativo
brand_color = "#996600"

st.markdown(f"""
    <style>
    .main {{ background-color: #f8f9fa; }}
    
    /* --- RESPONSIVE OPTIMIZATION --- */
    /* Título principal adaptable */
    .main-title {{
        font-size: 2.2rem;
        font-weight: bold;
        margin-bottom: 1rem;
    }}
    
    /* Ajustes para móviles (pantallas < 768px) */
    @media (max-width: 768px) {{
        .main-title {{ font-size: 1.5rem !important; }}
        .stImage img {{ width: 150px !important; }} /* Reducir logo en móvil */
        div[data-testid="stMetricValue"] {{ font-size: 1.4rem !important; }}
    }}

    /* --- ESTILOS DE MARCA (#996600) --- */
    /* Barras de progreso */
    .stProgress > div > div > div > div {{
        background-color: {brand_color};
    }}
    
    /* Pestañas (Tabs) */
    button[data-testid="stMarkdownContainer"] p {{ /* Texto de la pestaña */
        font-size: 1.1rem;
    }}
    
    /* Subrayado de pestaña activa */
    button[aria-selected="true"] {{
        border-bottom-color: {brand_color} !important;
    }}
    
    /* Hover (pasar el ratón) sobre pestañas */
    button[data-testid="stBaseButton-tab"]:hover {{
        color: {brand_color} !important;
    }}

    /* Métricas */
    div[data-testid="stMetricValue"] {{ color: {brand_color}; }}

    /* --- FOOTER/DISCLAIMER ESTILIZADO --- */
    .footer {{
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #ffffff;
        color: #555555;
        text-align: center;
        padding: 15px;
        font-size: 0.8rem;
        border-top: 1px solid #e0e0e0;
        z-index: 1000;
    }}
    </style>
    """, unsafe_allow_html=True)

# 2. SECCIÓN SUPERIOR: LOGO (Responsive vía CSS)
try:
    image = Image.open('Logo Academia-black (1).png')
    # Usamos un contenedor markdown para aplicar la clase responsive al logo si fuera necesario, 
    # pero st.image con width suele funcionar bien si el CSS global ayuda.
    st.image(image, width=220) # Un poco más pequeño por defecto
except FileNotFoundError:
    st.warning("Logo no encontrado. Sube 'Logo Academia-black (1).png' a la raíz de GitHub.")

# Título con clase CSS para responsive
st.markdown('<p class="main-title">📊 Simulador de Rentabilidad de Aparatología</p>', unsafe_allow_html=True)
st.markdown("---")

# --- 3. BARRA LATERAL (ENTRADAS) ---
with st.sidebar:
    st.header("🖊️ Identificación del Equipo")
    # TUS NUEVAS CASILLAS
    nombre_aparato = st.text_input("Nombre del Aparato", value="Ej: Láser Diodo")
    marca_aparato = st.text_input("Marca / Modelo", value="Ej: Impulxer Pro")
    
    st.markdown("---")
    st.header("📋 Datos de la Inversión")
    inv_sin_iva = st.number_input("Inversión Equipo (sin IVA)", value=15000.0, step=500.0)
    iva_pct = st.slider("IVA %", 0, 21, 21)
    costes_adic = st.number_input("Formación y otros costes", value=300.0)
    intereses = st.number_input("Intereses financiación", value=2000.0)
    
    st.header("⏱️ Capacidad de Trabajo")
    anos_amort = st.slider("Años de amortización", 1, 10, 5)
    semanas_ano = st.slider("Semanas laborales/año", 1, 52, 48)
    sesiones_sem_max = st.number_input("Capacidad máx. (sesiones/sem)", value=30)
    minutos_sesion = st.number_input("Minutos por sesión", value=60)

    st.header("💰 Estrategia de Precios")
    precio_sesion = st.number_input("Precio de venta sesión (€)", value=60.0)
    sesiones_reales_mes = st.slider("Sesiones reales al mes", 1, 100, 6)

# --- 4. CÁLCULOS MAESTROS (Sin cambios) ---
inv_total_iva = (inv_sin_iva * (1 + iva_pct/100)) + costes_adic + intereses
coste_anual = inv_total_iva / anos_amort
coste_mensual = coste_anual / 12
total_sesiones_teoricas = anos_amort * semanas_ano * sesiones_sem_max
coste_unitario_sesion = inv_total_iva / total_sesiones_teoricas
coste_minuto = coste_unitario_sesion / minutos_sesion
beneficio_sesion = precio_sesion - coste_unitario_sesion
margen_pct = (beneficio_sesion / precio_sesion) * 100
punto_equilibrio_mes = coste_mensual / precio_sesion
beneficio_mensual_real = (sesiones_reales_mes * precio_sesion) - coste_mensual

# --- 5. DASHBOARD PRINCIPAL ---
st.subheader(f"Análisis para: {nombre_aparato} ({marca_aparato})")

col1, col2, col3, col4 = st.columns(4)
col1.metric("Inversión Total", f"{inv_total_iva:,.2f} €")
col2.metric("Coste Mensual Fijo", f"{coste_mensual:,.2f} €")
col3.metric("Beneficio Mensual", f"{beneficio_mensual_real:,.2f} €")
col4.metric("¿Es Rentable?", "✅ SÍ" if beneficio_mensual_real > 0 else "❌ NO")

st.markdown("---")

tab1, tab2 = st.tabs(["🔍 Análisis Detallado", "📈 Escenarios de Crecimiento"])

with tab1:
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Costes Unitarios")
        st.write(f"**Coste por sesión (amortización):** {coste_unitario_sesion:.2f} €")
        st.write(f"**Coste por minuto de uso:** {coste_minuto:.4f} €")
        st.write(f"**Sesiones necesarias al mes para no perder:** {punto_equilibrio_mes:.2f}")
    with c2:
        st.subheader("Margen de Beneficio")
        st.write(f"**Beneficio por sesión:** {beneficio_sesion:.2f} €")
        st.write(f"**Margen Bruto sobre precio:** {margen_pct:.2f}%")
        # Barra de progreso con el color corporativo aplicado vía CSS
        st.progress(min(margen_pct/100, 1.0))

with tab2:
    st.subheader("Comparativa de Volumen de Sesiones")
    escenarios = [5, 10, 20, 30, 40, 50, 60]
    data_escenarios = []
    for s in escenarios:
        ingreso = s * precio_sesion
        ben = ingreso - coste_mensual
        rentable = "Sí" if ben > 0 else "No"
        ocupacion = (s / (sesiones_sem_max * 4)) * 100 if (sesiones_sem_max > 0) else 0
        data_escenarios.append([s, f"{ingreso:,.2f} €", f"{ben:,.2f} €", rentable, f"{ocupacion:.1f}%"])
    
    df = pd.DataFrame(data_escenarios, columns=["Sesiones/Mes", "Ingresos", "Beneficio Neto", "Rentable", "% Ocupación"])
    st.table(df)

    # Gráfico de barras (usa el color por defecto de streamlit, 
    # personalizar este color requiere librerías más complejas como Altair)
    st.subheader("Proyección de Beneficio Mensual")
    chart_data = pd.DataFrame({
        'Sesiones': [str(s) for s in escenarios],
        'Beneficio (€)': [(s * precio_sesion) - coste_mensual for s in escenarios]
    })
    st.bar_chart(data=chart_data, x='Sesiones', y='Beneficio (€)')

# --- 6. BOTÓN DE DESCARGA (ESTRUCTURA INICIAL) ---
st.markdown("---")
st.subheader("📥 Descargar Informe")
st.write("Pulsa el botón para generar un resumen de esta simulación en formato de texto (compatible con Excel/Word).")

# Crear el contenido del informe
informe_txt = f"""
INFORME DE RENTABILIDAD - IMPULXER ACADEMY
------------------------------------------
DATOS DEL EQUIPO:
Nombre: {nombre_aparato}
Marca/Modelo: {marca_aparato}

RESUMEN FINANCIERO:
Inversión Total (con IVA e intereses): {inv_total_iva:,.2f} €
Coste Mensual Fijo: {coste_mensual:,.2f} €
Precio de Venta por Sesión: {precio_sesion:,.2f} €

ESCENARIO ACTUAL ({sesiones_reales_mes} sesiones/mes):
Ingresos Mensuales: {sesiones_reales_mes * precio_sesion:,.2f} €
Beneficio Neto Mensual: {beneficio_mensual_real:,.2f} €
¿Rentable?: {"Sí" if beneficio_mensual_real > 0 else "No"}

ANÁLISIS DE COSTES:
Coste por sesión: {coste_unitario_sesion:.2f} €
Margen Bruto: {margen_pct:.2f}%
Sesiones/mes para punto de equilibrio: {punto_equilibrio_mes:.2f}

------------------------------------------
Disclaimer: Este informe es una simulación orientativa basada en los datos introducidos por el usuario. Impulxer Academy SL no se hace responsable de discrepancias con la realidad.
Propiedad de Impulxer Academy SL - 2026
"""

# Botón de descarga de Streamlit
st.download_button(
    label="💾 Descargar Informe (TXT)",
    data=informe_txt,
    file_name=f"ROI_{nombre_aparato.replace(' ','_')}.txt",
    mime="text/plain"
)


# --- 7. FOOTER/DISCLAIMER FIJO ---
st.markdown("""
    <div class="footer">
        Este simulador es solo orientativo. Impulxer Academy no se hace responsable de discrepancias con la realidad.
        Es responsabilidad del usuario introducir los datos con la mayor exactitud.
        <br><strong>Propiedad de Impulxer Academy SL - 2026</strong>
    </div>
    """, unsafe_allow_html=True)

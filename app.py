import streamlit as st
import pandas as pd
from PIL import Image

# 1. CONFIGURACIÓN DE PÁGINA Y ESTILOS
st.set_page_config(page_title="Calculadora ROI Pro", layout="wide")

# Estilos personalizados (CSS)
st.markdown("""
    <style>
    .main { background-color: #f8f9fa; }
    div[data-testid="stMetricValue"] { font-size: 1.8rem; color: #1f77b4; }
    
    /* Estilo para el disclaimer/footer inferior */
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: #f1f1f1;
        color: #555555;
        text-align: center;
        padding: 10px;
        font-size: 0.8rem;
        border-top: 1px solid #e0e0e0;
        z-index: 1000;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. SECCIÓN SUPERIOR: LOGO Y TÍTULO
# st.image("tu_logo.png", width=200) # Reemplaza con tu logo si lo tienes online
# Como tienes el logo en GitHub, puedes cargarlo directamente:
try:
    image = Image.open('Logo Academia-black (1).png')
    st.image(image, width=250)
except FileNotFoundError:
    st.warning("No se pudo cargar el logo. Asegúrate de que el archivo 'Logo Academia-black (1).png' esté en la raíz de tu repositorio de GitHub.")

st.title("🚀 Simulador de Rentabilidad: Inversión en Aparatología")
st.markdown("---")

# --- 3. BARRA LATERAL (ENTRADAS) ---
with st.sidebar:
    st.header("📋 Datos de la Inversión")
    inv_sin_iva = st.number_input("Inversión Equipo (sin IVA)", value=15000.0)
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

# --- 4. CÁLCULOS MAESTROS ---
inv_total_iva = (inv_sin_iva * (1 + iva_pct/100)) + costes_adic + intereses
coste_anual = inv_total_iva / anos_amort
coste_mensual = coste_anual / 12

# Capacidad teórica total
total_sesiones_teoricas = anos_amort * semanas_ano * sesiones_sem_max
coste_unitario_sesion = inv_total_iva / total_sesiones_teoricas
coste_minuto = coste_unitario_sesion / minutos_sesion

# Beneficio
beneficio_sesion = precio_sesion - coste_unitario_sesion
margen_pct = (beneficio_sesion / precio_sesion) * 100
punto_equilibrio_mes = coste_mensual / precio_sesion
beneficio_mensual_real = (sesiones_reales_mes * precio_sesion) - coste_mensual

# --- 5. DASHBOARD PRINCIPAL ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Inversión Total", f"{inv_total_iva:,.2f} €")
col2.metric("Coste Mensual Fijo", f"{coste_mensual:,.2f} €")
col3.metric("Beneficio Mensual", f"{beneficio_mensual_real:,.2f} €")
col4.metric("¿Es Rentable?", "✅ SÍ" if beneficio_mensual_real > 0 else "❌ NO")

st.markdown("---")

tab1, tab2 = st.tabs(["📊 Análisis Detallado", "📈 Escenarios de Crecimiento"])

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
        st.progress(min(margen_pct/100, 1.0))

with tab2:
    st.subheader("Comparativa de Escenarios")
    # Generar tabla de escenarios
    escenarios = [5, 10, 20, 30, 40, 50]
    data_escenarios = []
    for s in escenarios:
        ingreso = s * precio_sesion
        ben = ingreso - coste_mensual
        rentable = "Sí" if ben > 0 else "No"
        ocupacion = (s / (sesiones_sem_max * 4)) * 100
        data_escenarios.append([s, f"{ingreso:,.2f} €", f"{ben:,.2f} €", rentable, f"{ocupacion:.1f}%"])
    
    df = pd.DataFrame(data_escenarios, columns=["Sesiones/Mes", "Ingresos", "Beneficio Neto", "Rentable", "% Ocupación"])
    st.table(df)

    # Gráfico de barras de beneficio
    st.subheader("Proyección de Beneficio Mensual")
    chart_data = pd.DataFrame({
        'Sesiones': [str(s) for s in escenarios],
        'Beneficio (€)': [(s * precio_sesion) - coste_mensual for s in escenarios]
    })
    st.bar_chart(data=chart_data, x='Sesiones', y='Beneficio (€)')

# --- 6. SECCIÓN INFERIOR: DISCLAIMER/FOOTER (CSS FIJO) ---
st.markdown("""
    <div class="footer">
        Este simulador es solo orientativo. Impulxer Academy no se hace responsable de discrepancias con la realidad.
        Es responsabilidad del usuario introducir los datos con la mayor exactitud para que el resultado sea lo más real posible.
        <strong>Propiedad de Impulxer Academy SL - 2026</strong>
    </div>
    """, unsafe_allow_html=True)

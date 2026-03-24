import streamlit as st

st.set_page_config(page_title="Simulador ROI Aparatología", layout="wide")

# Estilo personalizado para que se vea más profesional
st.markdown("""
    <style>
    .main { background-color: #f5f7f9; }
    .stMetric { background-color: #ffffff; padding: 15px; border-radius: 10px; border: 1px solid #e0e0e0; }
    </style>
    """, unsafe_allow_html=True)

st.title("📊 Simulador de Inversión en Aparatología")
st.info("Configura los valores en la izquierda para ver el análisis de rentabilidad en tiempo real.")

# --- BARRA LATERAL (ENTRADAS) ---
with st.sidebar:
    st.header("⚙️ Configuración")
    
    st.subheader("Inversión")
    inv_sin_iva = st.number_input("Inversión (sin IVA)", value=15000.0, step=500.0)
    iva_pct = st.slider("IVA %", 0, 21, 21)
    costes_adic = st.number_input("Costes Adicionales (formación, etc)", value=300.0)
    intereses = st.number_input("Intereses totales", value=2000.0)
    
    st.subheader("Capacidad y Tiempo")
    anos_amort = st.number_input("Años de amortización", value=5)
    semanas_ano = st.slider("Semanas de trabajo al año", 1, 52, 48)
    sesiones_sem_cap = st.number_input("Capacidad máxima sesiones/semana", value=30)
    duracion_sesion = st.number_input("Duración sesión (minutos)", value=60)

    st.subheader("Venta Real")
    precio_sesion = st.number_input("Precio medio por sesión (€)", value=60.0)
    sesiones_mes_real = st.slider("Sesiones REALES al mes", 1, 120, 6)

# --- LÓGICA DE CÁLCULO (Réplica de tu Sheets) ---
inv_total_con_iva = (inv_sin_iva * (1 + iva_pct/100)) + costes_adic + intereses
coste_anual_total = inv_total_con_iva / anos_amort
coste_mensual_equipo = coste_anual_total / 12

# Coste por sesión basado en capacidad teórica (como en tu celda F24)
total_sesiones_teoricas_vida = anos_amort * semanas_ano * sesiones_sem_cap
coste_por_sesion = inv_total_con_iva / total_sesiones_teoricas_vida
coste_por_minuto = coste_por_sesion / duracion_sesion

# Resultados de venta real
ingresos_mensuales = sesiones_mes_real * precio_sesion
beneficio_mensual = ingresos_mensuales - coste_mensual_equipo
margen_bruto = ((precio_sesion - coste_por_sesion) / precio_sesion) * 100
sesiones_necesarias_punto_equilibrio = coste_mensual_equipo / precio_sesion

# --- VISUALIZACIÓN (DASHBOARD) ---
col1, col2, col3, col4 = st.columns(4)
col1.metric("Inversión Total", f"{inv_total_con_iva:,.2f} €")
col2.metric("Coste Mensual", f"{coste_mensual_equipo:,.2f} €")
col3.metric("Beneficio Mensual", f"{beneficio_mensual:,.2f} €", delta=f"{beneficio_mensual:,.2f} €")
col4.metric("¿Es Rentable?", "🟢 SÍ" if beneficio_mensual > 0 else "🔴 NO", delta_color="normal")

st.markdown("---")

c1, c2 = st.columns(2)

with c1:
    st.subheader("📈 Análisis de Amortización")
    st.write(f"**Sesiones mensuales para cubrir costes:** {sesiones_necesarias_punto_equilibrio:.2f}")
    st.write(f"**Beneficio estimado por sesión:** {precio_sesion - coste_por_sesion:.2f} €")
    st.write(f"**Margen Bruto:** {margen_bruto:.2f} %")
    
    progress_rel = min(sesiones_mes_real / sesiones_necesarias_punto_equilibrio, 1.0) if sesiones_necesarias_punto_equilibrio > 0 else 0
    st.write(f"Cobertura de costes fijos ({int(progress_rel*100)}%)")
    st.progress(progress_rel)

with c2:
    st.subheader("⏱️ Eficiencia Operativa")
    st.write(f"**Coste por sesión (amortización):** {coste_por_sesion:.2f} €")
    st.write(f"**Coste por minuto de uso:** {coste_por_minuto:.4f} €")
    st.write(f"**Ingresos anuales estimados:** {ingresos_mensuales * 12:,.2f} €")

st.markdown("---")
if beneficio_mensual < 0:
    st.warning("⚠️ El escenario actual no es rentable. Considera aumentar el precio por sesión o el volumen de clientes.")
else:
    st.success("🚀 ¡Inversión saludable! Cada sesión adicional después de la número " + str(round(sesiones_necesarias_punto_equilibrio,1)) + " es beneficio neto.")

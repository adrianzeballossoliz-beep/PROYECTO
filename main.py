import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# =====================================================
# CONFIGURACIÓN DE PÁGINA Y ESTILOS (Mantenidos tus estilos neón)
# =====================================================
st.set_page_config(
    page_title="Horizon Stay BI",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    body { background: linear-gradient(-45deg, #020202, #05070b, #071019, #020202); background-size: 500% 500%; animation: gradientBG 15s ease infinite; }
    @keyframes gradientBG { 0% {background-position: 0% 50%;} 50% {background-position: 100% 50%;} 100% {background-position: 0% 50%;} }
    h1 { font-size: 42px !important; font-weight: 900 !important; text-align: center; background: linear-gradient(90deg, #00f2ff, #00ff95, #ff00ea); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
    .stMetric { background: rgba(10, 15, 25, 0.75); backdrop-filter: blur(12px); padding: 25px; border-radius: 20px; border: 1px solid rgba(0,255,200,0.2); transition: 0.3s; }
    .stMetric:hover { transform: translateY(-5px); border-color: #00ff95; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# CONEXIÓN A BASE DE DATOS
# =====================================================
@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host="dpg-d72c1sua2pns73etkvc0-a.oregon-postgres.render.com",
        database="horizon_stay",
        user="horizon_stay_user",
        password="AqabpaGhhPpU21CGLWazFG0zNvPOO1tw",
        port="5432",
        sslmode="require"
    )

@st.cache_data(ttl=60) # Actualización cada minuto para datos OLAP
def run_query(query):
    try:
        conn = get_connection()
        return pd.read_sql(query, conn)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame()

# =====================================================
# SIDEBAR NAVEGACIÓN (8 CUBOS OLAP)
# =====================================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2983/2983973.png", width=70)
st.sidebar.title("Horizon Stay BI")
st.sidebar.markdown("---")

menu = st.sidebar.selectbox(
    "Selecciona un Cubo OLAP:",
    [
        "📊 Dashboard Ejecutivo",
        "💰 Análisis de Ingresos (Cubo 1)",
        "🛏️ Ocupación e Inventario (Cubo 2)",
        "✨ Servicios Premium (Cubo 3)",
        "🚚 Logística y Rutas (Cubo 4)",
        "👥 CRM y Fidelización (Cubo 5)",
        "📈 Marketing y Promos (Cubo 6)",
        "🎭 Eventos y Auditoría (Cubo 7-8)"
    ]
)

# =====================================================
# SECCIÓN 1: DASHBOARD EJECUTIVO (Resumen General)
# =====================================================
if menu == "📊 Dashboard Ejecutivo":
    st.title("Horizon Stay Business Intelligence")
    
    # KPIs rápidos usando funciones OLAP
    col1, col2, col3, col4 = st.columns(4)
    
    ingresos_total = run_query("SELECT SUM(total) FROM olap_rev_total_mensual()").iloc[0,0] or 0
    ticket_avg = run_query("SELECT * FROM olap_rev_ticket_promedio()").iloc[0,0] or 0
    puntos_total = run_query("SELECT * FROM olap_crm_puntos_acumulados_total()").iloc[0,0] or 0
    ratio_cancela = run_query("SELECT COUNT(*) FROM reserva WHERE estado_reserva='cancelada'").iloc[0,0]

    col1.metric("Ingresos Confirmados", f"{ingresos_total:,.2f} Bs")
    col2.metric("Ticket Promedio", f"{ticket_avg:,.2f} Bs")
    col3.metric("Puntos en Circulación", f"{puntos_total:,.0f} pts")
    col4.metric("Reservas Canceladas", ratio_cancela, delta_color="inverse")

    st.markdown("---")
    
    # Gráfico de Tendencia Mensual
    st.subheader("📈 Tendencia de Ingresos Mensuales")
    df_ventas = run_query("SELECT * FROM olap_rev_total_mensual()")
    fig_ventas = px.area(df_ventas, x='periodo', y='total', template="plotly_dark", color_discrete_sequence=['#00f2ff'])
    st.plotly_chart(fig_ventas, use_container_width=True)

# =====================================================
# SECCIÓN 2: CUBO 1 - ANÁLISIS FINANCIERO
# =====================================================
elif menu == "💰 Análisis de Ingresos (Cubo 1)":
    st.title("Análisis de Ingresos y Facturación")
    
    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Métodos de Pago Preferidos")
        df_pagos = run_query("SELECT * FROM olap_rev_por_metodo_pago()")
        fig_pagos = px.pie(df_pagos, values='total', names='metodo', hole=0.5, template="plotly_dark")
        st.plotly_chart(fig_pagos, use_container_width=True)
        
    with c2:
        st.subheader("Proyección de Ingresos Pendientes")
        df_pend = run_query("SELECT * FROM olap_rev_proyeccion_pendientes()")
        st.metric("Monto por Cobrar", f"{df_pend.iloc[0,0]:,.2f} Bs")
        st.info("Este monto corresponde a reservas en estado 'pendiente'.")

# =====================================================
# SECCIÓN 3: CUBO 2 - OCUPACIÓN
# =====================================================
elif menu == "🛏️ Ocupación e Inventario (Cubo 2)":
    st.title("Ocupación e Inventario")
    
    df_occ = run_query("SELECT * FROM olap_occ_por_tipo_habitacion()")
    fig_occ = px.bar(df_occ, x='tipo', y='total_reservas', color='total_reservas', template="plotly_dark", title="Reservas por Categoría")
    st.plotly_chart(fig_occ, use_container_width=True)
    
    col_a, col_b = st.columns(2)
    df_real = run_query("SELECT * FROM olap_occ_disponibilidad_real_time()")
    col_a.plotly_chart(px.pie(df_real, values='cantidad', names='estado', title="Estado Actual del Hotel"), use_container_width=True)
    
    df_piso = run_query("SELECT * FROM olap_occ_piso_mas_rentable()")
    col_b.plotly_chart(px.bar(df_piso, x='piso', y='ingresos', title="Rentabilidad por Piso"), use_container_width=True)

# =====================================================
# SECCIÓN 4: CUBO 4 - LOGÍSTICA
# =====================================================
elif menu == "🚚 Logística y Rutas (Cubo 4)":
    st.title("Logística de Transporte")
    
    df_rutas = run_query("SELECT * FROM olap_tra_rutas_mas_solicitadas()")
    fig_rutas = px.bar(df_rutas, x='cantidad', y='ruta_nombre', orientation='h', template="plotly_dark", color='cantidad')
    st.plotly_chart(fig_rutas, use_container_width=True)
    
    st.subheader("Estado de la Flota")
    df_flota = run_query("SELECT * FROM olap_tra_disponibilidad_vehicular()")
    st.table(df_flota)

# =====================================================
# SECCIÓN 5: CUBO 5 - CRM
# =====================================================
elif menu == "👥 CRM y Fidelización (Cubo 5)":
    st.title("Gestión de Clientes VIP")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("Segmentación por Nivel")
        df_niv = run_query("SELECT * FROM olap_crm_segmentacion_niveles()")
        st.plotly_chart(px.pie(df_niv, names='nivel', values='total_clientes', template="plotly_dark"), use_container_width=True)
        
    with col2:
        st.subheader("Top 10 Clientes VIP (Gasto)")
        df_gastadores = run_query("SELECT * FROM olap_crm_top_10_gastadores()")
        st.dataframe(df_gastadores, use_container_width=True)

# =====================================================
# SECCIÓN 6: CUBOS 7 Y 8 - AUDITORÍA
# =====================================================
elif menu == "🎭 Eventos y Auditoría (Cubo 7-8)":
    st.title("Control de Calidad y Auditoría")
    
    tab1, tab2 = st.tabs(["Eventos", "Auditoría Financiera"])
    
    with tab1:
        df_eve = run_query("SELECT * FROM olap_eve_ingresos_paquetes()")
        st.plotly_chart(px.funnel(df_eve, x='ingresos', y='paquete', title="Ingresos por Paquete de Eventos"), use_container_width=True)
        
    with tab2:
        df_audit = run_query("SELECT * FROM olap_aud_facturacion_vs_pagos()")
        st.subheader("Balance Facturación vs Pagos Reales")
        st.dataframe(df_audit)
        
        df_impagos = run_query("SELECT * FROM olap_aud_resumen_impagos()")
        st.warning("Lista de Clientes con Pagos Pendientes")
        st.dataframe(df_impagos)

# =====================================================
# FOOTER
# =====================================================
st.markdown("---")
st.caption(f"🚀 Sistema de Inteligencia de Negocios Horizon Stay | {datetime.now().strftime('%Y')} | Powered by PostgreSQL OLAP Functions")
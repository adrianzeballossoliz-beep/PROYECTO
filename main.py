# =====================================================
# HORIZON STAY - DASHBOARD BI ULTRA PROFESIONAL
# Fondo animado • Colores dinámicos • Diseño moderno • Interactivo
# =====================================================

import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# =====================================================
# 1. CONFIGURACIÓN GENERAL
# =====================================================

st.set_page_config(
    page_title="Horizon Stay | Business Intelligence",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 2. FONDO NEGRO ANIMADO (CAMBIO DE COLOR AUTOMÁTICO)
# =====================================================

st.markdown("""
<style>

/* Animación de fondo */
body {
    background: linear-gradient(-45deg, #05070b, #0b0f14, #0e1117, #06131a);
    background-size: 400% 400%;
    animation: gradientBG 12s ease infinite;
}

@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Fondo principal */
.main {
    background: transparent;
    color: white;
}

/* TÍTULO PRINCIPAL CON EFECTO NEÓN */
h1 {
    font-size: 44px !important;
    font-weight: 800 !important;
    text-align: center;
    background: linear-gradient(90deg, #00f2ff, #00ff95, #ff00ea);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

/* Subtítulos */
h2, h3 {
    color: #ffffff !important;
}

/* Tarjetas KPI tipo vidrio */
.stMetric {
    background: rgba(15, 20, 30, 0.7);
    backdrop-filter: blur(10px);
    padding: 25px;
    border-radius: 22px;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0px 10px 30px rgba(0,0,0,0.6);
    transition: 0.3s ease;
}

.stMetric:hover {
    transform: translateY(-6px);
    box-shadow: 0px 15px 40px rgba(0,255,200,0.25);
}

/* Sidebar con efecto oscuro elegante */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #020305, #06090f);
}

/* Botones con brillo */
.stButton > button {
    background: linear-gradient(90deg, #00f2ff, #00ff95);
    border: none;
    border-radius: 14px;
    padding: 12px 25px;
    font-weight: bold;
    color: black;
    transition: 0.3s ease;
}

.stButton > button:hover {
    transform: scale(1.05);
    box-shadow: 0px 0px 20px #00ffd0;
}

/* Radio botones */
.stRadio > div {
    background: rgba(15,20,30,0.6);
    padding: 15px;
    border-radius: 15px;
}

/* Dataframes */
.stDataFrame {
    background: rgba(10, 14, 20, 0.7);
    border-radius: 15px;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. CONEXIÓN A POSTGRESQL (MISMA CONEXIÓN)
# =====================================================

@st.cache_resource
def get_connection():
    try:
        conn = psycopg2.connect(
            host="dpg-d72c1sua2pns73etkvc0-a.oregon-postgres.render.com",
            database="horizon_stay",
            user="horizon_stay_user",
            password="AqabpaGhhPpU21CGLWazFG0zNvPOO1tw",
            port="5432",
            sslmode="require"
        )
        return conn
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return None

# =====================================================
# 4. FUNCIÓN GLOBAL PARA CONSULTAS
# =====================================================

@st.cache_data(ttl=300)
def run_query(query):
    conn = get_connection()
    if conn:
        return pd.read_sql(query, conn)
    return pd.DataFrame()

# =====================================================
# 5. SIDEBAR MODERNA
# =====================================================

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2983/2983973.png", width=120)
st.sidebar.title("Horizon Stay BI")
st.sidebar.markdown("### Inteligencia Empresarial del Hotel")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Selecciona una sección:",
    [
        "📊 Dashboard Ejecutivo",
        "🛏️ Inteligencia de Habitaciones",
        "💰 Análisis Financiero",
        "🍽️ Servicios Premium",
        "👥 Fidelidad de Clientes",
        "🚚 Transporte y Logística",
        "📈 Reporte Inteligente"
    ]
)

st.sidebar.markdown("---")
st.sidebar.success("Sistema activo")

# =====================================================
# 6. DASHBOARD PRINCIPAL (MUCHO MÁS BONITO)
# =====================================================

if menu == "📊 Dashboard Ejecutivo":

    st.title("Horizon Stay Business Intelligence")
    st.markdown("### Panel profesional con indicadores clave del negocio hotelero")

    col1, col2, col3, col4 = st.columns(4)

    ingresos = run_query("SELECT COALESCE(SUM(monto_total),0) FROM reserva WHERE estado_reserva='confirmada'").iloc[0,0]
    clientes = run_query("SELECT COUNT(*) FROM cliente").iloc[0,0]
    reservas = run_query("SELECT COUNT(*) FROM reserva").iloc[0,0]
    servicios = run_query("SELECT COUNT(*) FROM servicios_especiales").iloc[0,0]

    col1.metric("Ingresos Totales", f"{ingresos:,.0f} Bs")
    col2.metric("Clientes", clientes)
    col3.metric("Reservas", reservas)
    col4.metric("Servicios Premium", servicios)

    st.divider()

    # Gráfico 1
    df1 = run_query("SELECT estado_reserva, SUM(monto_total) as monto FROM reserva GROUP BY estado_reserva")
    fig1 = px.pie(df1, values='monto', names='estado_reserva', hole=0.6, template="plotly_dark")
    st.plotly_chart(fig1, use_container_width=True)

    # Gráfico 2
    df2 = run_query("SELECT fecha_reserva, monto_total FROM reserva ORDER BY fecha_reserva")
    if not df2.empty:
        fig2 = px.line(df2, x='fecha_reserva', y='monto_total', template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# 7. HABITACIONES
# =====================================================

elif menu == "🛏️ Inteligencia de Habitaciones":

    st.title("Análisis Inteligente de Habitaciones")

    df = run_query("""
        SELECT t.tipo_cama, t.capacidad, COUNT(h.id_habitacion) as cantidad
        FROM habitacion h
        JOIN tipo_habitacion t ON h.id_tipo_habitacion = t.id_tipo_habitacion
        GROUP BY t.tipo_cama, t.capacidad
    """)

    fig = px.bar(df, x='tipo_cama', y='cantidad', color='capacidad', template="plotly_dark", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True)

# =====================================================
# 8. ANÁLISIS FINANCIERO
# =====================================================

elif menu == "💰 Análisis Financiero":

    st.title("Análisis Financiero Profesional")

    df = run_query("SELECT estado_reserva, monto_total FROM reserva")

    fig = px.box(df, x='estado_reserva', y='monto_total', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.histogram(df, x='monto_total', template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# 9. SERVICIOS
# =====================================================

elif menu == "🍽️ Servicios Premium":

    st.title("Servicios Premium del Hotel")

    df = run_query("""
        SELECT s.nombre, SUM(d.precio_unitario) as total
        FROM detalle_reserva_servicios_especiales d
        JOIN servicios_especiales s ON d.id_servicios_especiales = s.id_servicios_especiales
        GROUP BY s.nombre
        ORDER BY total DESC
    """)

    fig = px.funnel(df, x='total', y='nombre', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True)

# =====================================================
# 10. FIDELIDAD
# =====================================================

elif menu == "👥 Fidelidad de Clientes":

    st.title("Clientes VIP")

    df = run_query("""
        SELECT c.nombre || ' ' || c.apellido_paterno as cliente, cf.puntos_acumulados
        FROM cliente c
        JOIN cliente_fidelidad cf ON c.id_cliente = cf.id_cliente_fidelidad
        ORDER BY cf.puntos_acumulados DESC
        LIMIT 10
    """)

    fig = px.line(df, x='cliente', y='puntos_acumulados', markers=True, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True)

# =====================================================
# 11. TRANSPORTE
# =====================================================

elif menu == "🚚 Transporte y Logística":

    st.title("Logística del Hotel")

    df = run_query("""
        SELECT r.origen || ' ➡️ ' || r.destino as trayecto, SUM(r.tarifa) as recaudacion
        FROM transporte_ruta tr
        JOIN ruta r ON tr.id_ruta = r.id_ruta
        GROUP BY trayecto
        ORDER BY recaudacion DESC
    """)

    fig = px.bar(df, x='recaudacion', y='trayecto', orientation='h', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True)

# =====================================================
# 12. FOOTER
# =====================================================

st.markdown("---")
st.markdown("### Horizon Stay Business Intelligence Dashboard")
st.caption(f"Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

# =====================================================
# HORIZON STAY - DASHBOARD BI ULTRA PROFESIONAL 2.0
# Diseño extremo • Fondo dinámico • Interactividad avanzada • UI moderna
# =====================================================

import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import numpy as np

# =====================================================
# 1. CONFIGURACIÓN GENERAL
# =====================================================

st.set_page_config(
    page_title="Horizon Stay | Business Intelligence PRO",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# =====================================================
# 2. FONDO NEGRO ULTRA ANIMADO + EFECTOS VISUALES
# =====================================================

st.markdown("""
<style>

/* Fondo animado profesional tipo Power BI oscuro */
body {
    background: linear-gradient(-45deg, #020202, #05070b, #071019, #020202);
    background-size: 500% 500%;
    animation: gradientBG 15s ease infinite;
}

@keyframes gradientBG {
    0% {background-position: 0% 50%;}
    50% {background-position: 100% 50%;}
    100% {background-position: 0% 50%;}
}

/* Partículas simuladas */
.main::before {
    content: "";
    position: fixed;
    top: 0;
    left: 0;
    width: 100%;
    height: 100%;
    background: radial-gradient(circle at 20% 30%, rgba(0,255,200,0.05), transparent 40%),
                radial-gradient(circle at 80% 70%, rgba(0,140,255,0.05), transparent 40%),
                radial-gradient(circle at 50% 50%, rgba(255,0,200,0.05), transparent 40%);
    z-index: -1;
}

/* TÍTULO NEÓN */
h1 {
    font-size: 48px !important;
    font-weight: 900 !important;
    text-align: center;
    background: linear-gradient(90deg, #00f2ff, #00ff95, #ff00ea);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    letter-spacing: 1px;
}

/* Subtítulo */
h2, h3 {
    color: white !important;
}

/* TARJETAS KPI MEJORADAS */
.stMetric {
    background: rgba(10, 15, 25, 0.75);
    backdrop-filter: blur(12px);
    padding: 30px;
    border-radius: 25px;
    border: 1px solid rgba(255,255,255,0.1);
    box-shadow: 0px 12px 35px rgba(0,0,0,0.7);
    transition: 0.35s ease;
}

.stMetric:hover {
    transform: translateY(-10px) scale(1.02);
    box-shadow: 0px 18px 50px rgba(0,255,200,0.25);
}

/* SIDEBAR PRO */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #010101, #04070c);
}

/* BOTONES ULTRA INTERACTIVOS */
.stButton > button {
    background: linear-gradient(90deg, #00f2ff, #00ff95);
    border-radius: 14px;
    padding: 14px 26px;
    border: none;
    font-weight: bold;
    color: black;
    transition: 0.3s ease;
}

.stButton > button:hover {
    transform: scale(1.07);
    box-shadow: 0px 0px 25px #00ffd0;
}

/* TABLAS BONITAS */
.stDataFrame {
    background: rgba(10,14,20,0.75);
    border-radius: 20px;
}

/* RADIO BUTTON PRO */
.stRadio > div {
    background: rgba(10,15,25,0.7);
    padding: 15px;
    border-radius: 15px;
}

/* DIVIDER NEÓN */
hr {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, #00ffd0, transparent);
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# 3. CONEXIÓN A POSTGRESQL
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

# =====================================================
# 4. FUNCIÓN GLOBAL CONSULTAS
# =====================================================

@st.cache_data(ttl=300)
def run_query(query):
    conn = get_connection()
    return pd.read_sql(query, conn)

# =====================================================
# 5. SIDEBAR MODERNA
# =====================================================

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2983/2983973.png", width=80)
st.sidebar.title("Horizon Stay")
st.sidebar.markdown("### Inteligencia Empresarial del Hotel")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Selecciona una sección:",
    [
        "📊 Dashboard Ejecutivo",
        "🛏️ Habitaciones Inteligentes",
        "💰 Análisis Financiero",
        "🍽️ Servicios Premium",
        "👥 Fidelidad de Clientes",
        "🚚 Transporte y Logística",
        "📈 Reporte Inteligente"
    ]
)

# =====================================================
# 6. DASHBOARD EJECUTIVO ULTRA PRO
# =====================================================

if menu == "📊 Dashboard Ejecutivo":

    st.title("Horizon Stay Business Intelligence")
    st.markdown("### Panel avanzado con analítica en tiempo real")

    col1, col2, col3, col4 = st.columns(4)

    ingresos = run_query("SELECT COALESCE(SUM(monto_total),0) FROM reserva WHERE estado_reserva='confirmada'").iloc[0,0]
    clientes = run_query("SELECT COUNT(*) FROM cliente").iloc[0,0]
    reservas = run_query("SELECT COUNT(*) FROM reserva").iloc[0,0]
    servicios = run_query("SELECT COUNT(*) FROM servicios_especiales").iloc[0,0]

    col1.metric("Ingresos Totales", f"{ingresos:,.0f} Bs")
    col2.metric("Clientes", clientes)
    col3.metric("Reservas", reservas)
    col4.metric("Servicios Premium", servicios)

    st.markdown("---")

    # GRÁFICO DONUT PROFESIONAL
    df1 = run_query("SELECT estado_reserva, SUM(monto_total) as monto FROM reserva GROUP BY estado_reserva")

    fig1 = px.pie(
        df1,
        values='monto',
        names='estado_reserva',
        hole=0.65,
        template="plotly_dark"
    )

    fig1.update_traces(textfont_size=14)
    st.plotly_chart(fig1, use_container_width=True)

    # GRÁFICO LINEA ANIMADO
    df2 = run_query("SELECT fecha_reserva, monto_total FROM reserva ORDER BY fecha_reserva")

    fig2 = px.line(df2, x='fecha_reserva', y='monto_total', template="plotly_dark")
    fig2.update_traces(mode='lines+markers')
    st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# 7. HABITACIONES INTELIGENTES
# =====================================================

elif menu == "🛏️ Habitaciones Inteligentes":

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
# 8. ANÁLISIS FINANCIERO PRO
# =====================================================

elif menu == "💰 Análisis Financiero":

    st.title("Análisis Financiero Profesional")

    df = run_query("SELECT estado_reserva, monto_total FROM reserva")

    fig = px.box(df, x='estado_reserva', y='monto_total', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.histogram(df, x='monto_total', template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)

# =====================================================
# 9. SERVICIOS PREMIUM
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
# 10. FIDELIDAD DE CLIENTES
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
# 11. TRANSPORTE Y LOGÍSTICA
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
# 12. FOOTER DINÁMICO
# =====================================================

st.markdown("---")
st.markdown("### Horizon Stay Business Intelligence Dashboard")
st.caption(f"Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

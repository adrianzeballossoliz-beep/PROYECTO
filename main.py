# =====================================================
# HORIZON STAY - DASHBOARD BI PROFESIONAL (VERSIÓN MEJORADA)
# Más color • Más interacción • Más diseño • Más profesional
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
# 2. CSS ULTRA PROFESIONAL (MUCHO MÁS COLOR Y DISEÑO)
# =====================================================

st.markdown("""
<style>

/* Fondo general */
.main {
    background: linear-gradient(180deg, #0b0f14 0%, #0e1117 100%);
    color: white;
}

/* Títulos */
h1 {
    font-size: 40px !important;
    font-weight: 700 !important;
    background: linear-gradient(90deg, #00f2ff, #00ff95);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}

h2, h3 {
    color: #ffffff !important;
}

/* Tarjetas KPI */
.stMetric {
    background: linear-gradient(145deg, #11161d, #0b0f14);
    padding: 25px;
    border-radius: 20px;
    border: 1px solid #2a2f3a;
    box-shadow: 0px 8px 20px rgba(0,0,0,0.6);
    transition: 0.3s ease-in-out;
}

.stMetric:hover {
    transform: scale(1.03);
    box-shadow: 0px 10px 25px rgba(0,255,180,0.2);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #05080d, #0b0f14);
}

/* Botones */
.stButton > button {
    background: linear-gradient(90deg, #00f2ff, #00ff95);
    border: none;
    border-radius: 12px;
    padding: 10px 20px;
    font-weight: bold;
    color: black;
}

/* Radio */
.stRadio > div {
    background-color: #11161d;
    padding: 15px;
    border-radius: 15px;
}

/* Dataframes */
.stDataFrame {
    background-color: #11161d;
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
# 4. FUNCIÓN GLOBAL PARA CONSULTAS SQL
# =====================================================

@st.cache_data(ttl=300)
def run_query(query):
    conn = get_connection()
    if conn:
        return pd.read_sql(query, conn)
    return pd.DataFrame()


# =====================================================
# 5. SIDEBAR PROFESIONAL
# =====================================================

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2983/2983973.png", width=120)
st.sidebar.title("Horizon Stay BI")
st.sidebar.markdown("### Dashboard Profesional de Inteligencia Empresarial")
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
        "📈 Reporte Avanzado"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("Proyecto Profesional - Base de Datos II")


# =====================================================
# 6. DASHBOARD EJECUTIVO (MÁS INTERACTIVO)
# =====================================================

if menu == "📊 Dashboard Ejecutivo":

    st.title("Dashboard Ejecutivo Horizon Stay")
    st.markdown("### Panel principal con indicadores clave del hotel")

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

    # ----- GRAFICO 1 -----
    df1 = run_query("SELECT estado_reserva, SUM(monto_total) as monto FROM reserva GROUP BY estado_reserva")

    fig1 = px.pie(df1, values='monto', names='estado_reserva', hole=0.6, template="plotly_dark")
    st.plotly_chart(fig1, use_container_width=True)

    # ----- GRAFICO 2 -----
    df2 = run_query("SELECT fecha_reserva, monto_total FROM reserva ORDER BY fecha_reserva")

    if not df2.empty:
        fig2 = px.line(df2, x='fecha_reserva', y='monto_total', template="plotly_dark")
        st.plotly_chart(fig2, use_container_width=True)


# =====================================================
# 7. INTELIGENCIA DE HABITACIONES
# =====================================================

elif menu == "🛏️ Inteligencia de Habitaciones":

    st.title("Análisis Inteligente de Habitaciones")

    query = """
        SELECT t.tipo_cama, t.capacidad, COUNT(h.id_habitacion) as cantidad
        FROM habitacion h
        JOIN tipo_habitacion t ON h.id_tipo_habitacion = t.id_tipo_habitacion
        GROUP BY t.tipo_cama, t.capacidad
    """

    df = run_query(query)

    fig = px.bar(df, x='tipo_cama', y='cantidad', color='capacidad', template="plotly_dark", text_auto=True)
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True)


# =====================================================
# 8. ANÁLISIS FINANCIERO
# =====================================================

elif menu == "💰 Análisis Financiero":

    st.title("Análisis Financiero del Hotel")

    df = run_query("SELECT estado_reserva, monto_total FROM reserva")

    fig = px.box(df, x='estado_reserva', y='monto_total', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    fig2 = px.histogram(df, x='monto_total', template="plotly_dark")
    st.plotly_chart(fig2, use_container_width=True)


# =====================================================
# 9. SERVICIOS PREMIUM
# =====================================================

elif menu == "🍽️ Servicios Premium":

    st.title("Análisis de Servicios Premium")

    query = """
        SELECT s.nombre, SUM(d.precio_unitario) as total
        FROM detalle_reserva_servicios_especiales d
        JOIN servicios_especiales s ON d.id_servicios_especiales = s.id_servicios_especiales
        GROUP BY s.nombre
        ORDER BY total DESC
    """

    df = run_query(query)

    fig = px.funnel(df, x='total', y='nombre', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True)


# =====================================================
# 10. FIDELIDAD DE CLIENTES
# =====================================================

elif menu == "👥 Fidelidad de Clientes":

    st.title("Clientes VIP y Fidelización")

    query = """
        SELECT c.nombre || ' ' || c.apellido_paterno as cliente, cf.puntos_acumulados
        FROM cliente c
        JOIN cliente_fidelidad cf ON c.id_cliente = cf.id_cliente_fidelidad
        ORDER BY cf.puntos_acumulados DESC
        LIMIT 10
    """

    df = run_query(query)

    fig = px.line(df, x='cliente', y='puntos_acumulados', markers=True, template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True)


# =====================================================
# 11. TRANSPORTE Y LOGÍSTICA
# =====================================================

elif menu == "🚚 Transporte y Logística":

    st.title("Logística de Transporte")

    query = """
        SELECT r.origen || ' ➡️ ' || r.destino as trayecto, SUM(r.tarifa) as recaudacion
        FROM transporte_ruta tr
        JOIN ruta r ON tr.id_ruta = r.id_ruta
        GROUP BY trayecto
        ORDER BY recaudacion DESC
    """

    df = run_query(query)

    fig = px.bar(df, x='recaudacion', y='trayecto', orientation='h', template="plotly_dark")
    st.plotly_chart(fig, use_container_width=True)

    st.dataframe(df, use_container_width=True)


# =====================================================
# 12. REPORTE AVANZADO (NUEVA SECCIÓN MÁS INTERACTIVA)
# =====================================================

elif menu == "📈 Reporte Avanzado":

    st.title("Reporte Avanzado de Datos")

    tabla = st.selectbox(
        "Selecciona una tabla para analizar",
        ["cliente", "reserva", "habitacion", "servicios_especiales"]
    )

    df = run_query(f"SELECT * FROM {tabla}")

    st.dataframe(df, use_container_width=True)

    if not df.empty:
        columna = st.selectbox("Selecciona una columna numérica", df.select_dtypes(include='number').columns)

        fig = px.histogram(df, x=columna, template="plotly_dark")
        st.plotly_chart(fig, use_container_width=True)


# =====================================================
# 13. FOOTER PROFESIONAL
# =====================================================

st.markdown("---")
st.markdown("### Horizon Stay Business Intelligence Dashboard")
st.caption(f"Actualizado: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

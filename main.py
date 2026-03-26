import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# =====================================================
# 1. CONFIGURACIÓN GENERAL Y DISEÑO
# =====================================================

st.set_page_config(
    page_title="Horizon Stay | Business Intelligence",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------- CSS MEJORADO (más profesional y limpio) ----------
st.markdown("""
<style>

/* Fondo general */
.main {
    background-color: #0e1117;
    color: white;
}

/* Tarjetas KPI */
.stMetric {
    background: linear-gradient(145deg, #161b22, #11161d);
    padding: 22px;
    border-radius: 18px;
    border: 1px solid #30363d;
    box-shadow: 0px 6px 15px rgba(0,0,0,0.5);
    transition: 0.3s ease-in-out;
}

.stMetric:hover {
    transform: scale(1.02);
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background-color: #0b0f14;
}

/* Títulos principales */
h1, h2, h3 {
    color: #ffffff;
}

/* Botones y radio */
.stRadio > div {
    background-color: #11161d;
    padding: 10px;
    border-radius: 12px;
}

</style>
""", unsafe_allow_html=True)


# =====================================================
# 2. CONEXIÓN A POSTGRESQL (MISMA CONEXIÓN - OPTIMIZADA)
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
# 3. FUNCIÓN REUTILIZABLE PARA CONSULTAS SQL
# =====================================================

@st.cache_data(ttl=300)
def run_query(query):
    conn = get_connection()
    if conn:
        return pd.read_sql(query, conn)
    return pd.DataFrame()


# =====================================================
# 4. SIDEBAR (MISMO OBJETIVO PERO MÁS PROFESIONAL)
# =====================================================

st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2983/2983973.png", width=110)
st.sidebar.title("Horizon Stay BI")
st.sidebar.markdown("### Panel de Inteligencia Empresarial")
st.sidebar.markdown("---")

menu = st.sidebar.radio(
    "Seleccione un Cubo OLAP:",
    [
        "📊 Vista General",
        "🛏️ Análisis de Habitaciones",
        "🍽️ Servicios Especiales",
        "👥 Fidelidad de Clientes",
        "🚚 Logística y Rutas"
    ]
)

st.sidebar.markdown("---")
st.sidebar.info("Proyecto Académico - Base de Datos II")


# =====================================================
# 5. VISTA GENERAL (KPIs + RESUMEN EJECUTIVO)
# =====================================================

if menu == "📊 Vista General":

    st.title("📈 Dashboard Ejecutivo - Horizon Stay")
    st.markdown("### Indicadores clave del negocio hotelero")

    col1, col2, col3, col4 = st.columns(4)

    ingresos = run_query("""
        SELECT COALESCE(SUM(monto_total),0) as total
        FROM reserva
        WHERE estado_reserva = 'confirmada'
    """).iloc[0,0]

    clientes = run_query("SELECT COUNT(*) FROM cliente").iloc[0,0]
    reservas = run_query("SELECT COUNT(*) FROM reserva").iloc[0,0]

    col1.metric("Ingresos Totales", f"{ingresos:,.0f} Bs")
    col2.metric("Clientes Registrados", clientes)
    col3.metric("Reservas Totales", reservas)
    col4.metric("Estado del Sistema", "Online")

    st.divider()

    # ---------- Cubo OLAP 1 ----------
    st.subheader("Distribución Financiera por Estado de Reserva")

    df1 = run_query("""
        SELECT estado_reserva, SUM(monto_total) as monto
        FROM reserva
        GROUP BY estado_reserva
    """)

    fig1 = px.pie(
        df1,
        values='monto',
        names='estado_reserva',
        hole=0.55,
        template="plotly_dark"
    )

    st.plotly_chart(fig1, use_container_width=True)


# =====================================================
# 6. ANÁLISIS DE HABITACIONES
# =====================================================

elif menu == "🛏️ Análisis de Habitaciones":

    st.title("🏨 Inteligencia de Alojamiento")
    st.markdown("### Preferencias y capacidad de habitaciones")

    query2 = """
        SELECT t.tipo_cama,
               COUNT(h.id_habitacion) as cantidad,
               t.capacidad
        FROM habitacion h
        JOIN tipo_habitacion t ON h.id_tipo_habitacion = t.id_tipo_habitacion
        GROUP BY t.tipo_cama, t.capacidad
    """

    df2 = run_query(query2)

    fig2 = px.bar(
        df2,
        x='tipo_cama',
        y='cantidad',
        color='capacidad',
        text_auto=True,
        template="plotly_dark"
    )

    st.plotly_chart(fig2, use_container_width=True)
    st.dataframe(df2, use_container_width=True)


# =====================================================
# 7. SERVICIOS ESPECIALES
# =====================================================

elif menu == "🍽️ Servicios Especiales":

    st.title("✨ Rentabilidad de Servicios Especiales")

    query3 = """
        SELECT s.nombre,
               SUM(d.precio_unitario) as total
        FROM detalle_reserva_servicios_especiales d
        JOIN servicios_especiales s ON d.id_servicios_especiales = s.id_servicios_especiales
        GROUP BY s.nombre
        ORDER BY total DESC
    """

    df3 = run_query(query3)

    fig3 = px.funnel(
        df3,
        x='total',
        y='nombre',
        template="plotly_dark"
    )

    st.plotly_chart(fig3, use_container_width=True)


# =====================================================
# 8. FIDELIDAD DE CLIENTES
# =====================================================

elif menu == "👥 Fidelidad de Clientes":

    st.title("🏆 Programa de Fidelización")

    query4 = """
        SELECT c.nombre || ' ' || c.apellido_paterno as cliente,
               cf.puntos_acumulados
        FROM cliente c
        JOIN cliente_fidelidad cf
        ON c.id_cliente = cf.id_cliente_fidelidad
        ORDER BY cf.puntos_acumulados DESC
        LIMIT 10
    """

    df4 = run_query(query4)

    fig4 = px.line(
        df4,
        x='cliente',
        y='puntos_acumulados',
        markers=True,
        template="plotly_dark"
    )

    st.plotly_chart(fig4, use_container_width=True)
    st.dataframe(df4, use_container_width=True)


# =====================================================
# 9. LOGÍSTICA Y RUTAS
# =====================================================

elif menu == "🚚 Logística y Rutas":

    st.title("🚌 Gestión de Transporte y Rutas")

    query5 = """
        SELECT r.origen || ' ➡️ ' || r.destino as trayecto,
               SUM(r.tarifa) as recaudacion
        FROM transporte_ruta tr
        JOIN ruta r ON tr.id_ruta = r.id_ruta
        GROUP BY trayecto
        ORDER BY recaudacion DESC
    """

    df5 = run_query(query5)

    fig5 = px.bar(
        df5,
        x='recaudacion',
        y='trayecto',
        orientation='h',
        template="plotly_dark"
    )

    st.plotly_chart(fig5, use_container_width=True)
    st.dataframe(df5, use_container_width=True)


# =====================================================
# 10. FOOTER PROFESIONAL
# =====================================================

st.markdown("---")
st.markdown("### Horizon Stay Business Intelligence Dashboard")
st.caption(f"Última actualización: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")

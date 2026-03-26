import streamlit as st
import pandas as pd
import psycopg2 
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# --- 1. CONFIGURACIÓN E ESTÉTICA ---
st.set_page_config(
    page_title="Horizon Stay | Business Intelligence",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Inyección de CSS para personalización visual
st.markdown("""
    <style>
    .main { background-color: #0e1117; color: white; }
    .stMetric { 
        background-color: #161b22; 
        padding: 20px; 
        border-radius: 15px; 
        border: 1px solid #30363d;
        box-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    div[data-testid="stExpander"] { border: none !important; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. GESTIÓN DE CONEXIÓN ---
def get_connection():
    try:
        return psycopg2.connect(
            host="localhost", # Esto funcionará cuando lo corras en tu PC
            database="postgres", 
            user="postgres",
            password="123456", 
            port="5432"
        )
    except Exception:
        # Esto evita que la app de Streamlit Cloud se rompa al no encontrar tu PC
        return None

# --- 3. MENÚ LATERAL (REQUISITO DEL PDF)  ---
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2983/2983973.png", width=120)
st.sidebar.title("Horizon Stay BI")
st.sidebar.markdown("---")
menu = st.sidebar.radio(
    "Seleccione un Cubo OLAP:",
    ["📊 Vista General", "🛏️ Análisis de Habitaciones", "🍽️ Servicios Especiales", "👥 Fidelidad de Clientes", "🚚 Logística y Rutas"]
)

st.sidebar.markdown("---")
st.sidebar.info("Proyecto: Primera Parte\nAsignatura: Base de Datos II")

# --- 4. CUERPO PRINCIPAL ---
conn = get_connection()

if conn:
    if menu == "📊 Vista General":
        st.title("📈 Dashboard Ejecutivo - Vista General")
        
        # Métricas principales (KPIs)
        col1, col2, col3, col4 = st.columns(4)
        ingresos = pd.read_sql("SELECT SUM(monto_total) FROM reserva WHERE estado_reserva = 'confirmada'", conn).iloc[0,0] or 0
        clientes = pd.read_sql("SELECT COUNT(*) FROM cliente", conn).iloc[0,0]
        reservas = pd.read_sql("SELECT COUNT(*) FROM reserva", conn).iloc[0,0]
        
        col1.metric("Ingresos Totales", f"{ingresos} Bs", "+15%")
        col2.metric("Total Clientes", clientes, "Activos")
        col3.metric("Reservas Registradas", reservas)
        col4.metric("Sistema", "Online", delta_color="normal")

        st.divider()
        
        # Cubo OLAP 1: Flujo de Ingresos por Estado [cite: 34, 51]
        st.subheader("Cubo OLAP 1: Distribución Financiera por Estado de Reserva")
        df1 = pd.read_sql("SELECT estado_reserva, SUM(monto_total) as monto FROM reserva GROUP BY estado_reserva", conn)
        fig1 = px.pie(df1, values='monto', names='estado_reserva', hole=0.5, color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig1, use_container_width=True)

    elif menu == "🛏️ Análisis de Habitaciones":
        st.title("🏨 Inteligencia de Alojamiento")
        
        # Cubo OLAP 2: Demanda por Tipo de Habitación [cite: 34, 51]
        st.subheader("Cubo OLAP 2: Preferencia de Habitaciones y Capacidad")
        query2 = """
            SELECT t.tipo_cama, COUNT(h.id_habitacion) as cantidad, t.capacidad
            FROM habitacion h 
            JOIN tipo_habitacion t ON h.id_tipo_habitacion = t.id_tipo_habitacion 
            GROUP BY t.tipo_cama, t.capacidad
        """
        df2 = pd.read_sql(query2, conn)
        fig2 = px.bar(df2, x='tipo_cama', y='cantidad', color='capacidad', barmode='group', text_auto=True)
        st.plotly_chart(fig2, use_container_width=True)

    elif menu == "🍽️ Servicios Especiales":
        st.title("✨ Análisis de Servicios y Experiencias")
        
        # Cubo OLAP 3: Rentabilidad de Servicios [cite: 34, 51]
        st.subheader("Cubo OLAP 3: Embudo de Rentabilidad por Servicio")
        query3 = """
            SELECT s.nombre, SUM(d.precio_unitario) as total
            FROM detalle_reserva_servicios_especiales d
            JOIN servicios_especiales s ON d.id_servicios_especiales = s.id_servicios_especiales
            GROUP BY s.nombre ORDER BY total DESC
        """
        df3 = pd.read_sql(query3, conn)
        fig3 = px.funnel(df3, x='total', y='nombre', color='total')
        st.plotly_chart(fig3, use_container_width=True)

    elif menu == "👥 Fidelidad de Clientes":
        st.title("🏆 Programa de Fidelización")
        
        # Cubo OLAP 4: Segmentación de Clientes [cite: 34, 51]
        st.subheader("Cubo OLAP 4: Ranking de Clientes y Puntos Acumulados")
        query4 = """
            SELECT c.nombre || ' ' || c.apellido_paterno as cliente, cf.puntos_acumulados 
            FROM cliente c 
            JOIN cliente_fidelidad cf ON c.id_cliente = cf.id_cliente_fidelidad
            ORDER BY cf.puntos_acumulados DESC LIMIT 10
        """
        df4 = pd.read_sql(query4, conn)
        fig4 = px.line(df4, x='cliente', y='puntos_acumulados', markers=True, title="Top 10 Clientes VIP")
        st.plotly_chart(fig4, use_container_width=True)
        st.dataframe(df4, use_container_width=True)

    elif menu == "🚚 Logística y Rutas":
        st.title("🚌 Gestión de Transporte y Rutas")
        
        # Cubo OLAP 5: Eficiencia de Rutas [cite: 34, 51]
        st.subheader("Cubo OLAP 5: Recaudación por Trayecto")
        query5 = """
            SELECT r.origen || ' ➡️ ' || r.destino as trayecto, SUM(r.tarifa) as recaudacion
            FROM transporte_ruta tr
            JOIN ruta r ON tr.id_ruta = r.id_ruta
            GROUP BY trayecto
        """
        df5 = pd.read_sql(query5, conn)
        fig5 = px.bar(df5, y='trayecto', x='recaudacion', orientation='h', color='recaudacion')
        st.plotly_chart(fig5, use_container_width=True)

    conn.close()
else:
    st.error("No se pudo conectar a la base de datos. Verifica que el servicio de PostgreSQL esté activo.")
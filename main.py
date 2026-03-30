import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
from datetime import datetime

# =====================================================
# 1. CONFIGURACIÓN Y ESTILO VISUAL NEÓN
# =====================================================
st.set_page_config(page_title="Horizon Stay BI - Pro", page_icon="🏨", layout="wide")

st.markdown("""
<style>
    body { background-color: #020202; }
    .stApp {
        background: radial-gradient(circle at top right, #071019, #020202);
    }
    h1 { 
        font-size: 45px !important; 
        font-weight: 900 !important; 
        text-align: center; 
        background: linear-gradient(90deg, #00f2ff, #7000ff, #00ff95); 
        -webkit-background-clip: text; 
        -webkit-text-fill-color: transparent;
        text-shadow: 0px 10px 20px rgba(0,242,255,0.3);
    }
    h2, h3 { color: #00ffd0 !important; text-shadow: 0 0 10px rgba(0,255,208,0.5); }
    .stMetric { 
        background: rgba(10, 15, 25, 0.6); 
        backdrop-filter: blur(12px); 
        padding: 25px; 
        border-radius: 15px; 
        border: 1px solid rgba(0,255,200,0.3); 
        box-shadow: 0 8px 32px 0 rgba(0,0,0,0.8);
    }
    [data-testid="stSidebar"] { 
        background: #010101; 
        border-right: 2px solid #7000ff; 
    }
    .stDataFrame { border: 1px solid #7000ff; border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# =====================================================
# 2. CONEXIÓN A LA BASE DE DATOS (RENDER)
# =====================================================
@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host="localhost",           # Cambiado a servidor local
        database="postgres",    # Asegúrate de que el nombre sea igual en tu pgAdmin/DBeaver
        user="postgres",            # Usuario por defecto de PostgreSQL local
        password="123456",   # La contraseña que configuraste al instalar Postgres
        port="5432"                 # Puerto estándar
        # sslmode="require"         # Generalmente no es necesario en localhost
    )

def run_query(query):
    try:
        conn = get_connection()
        # Nota: pd.read_sql suele requerir cerrar la conexión o usar un context manager
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"⚠️ Error de Conexión/Consulta Local: {e}")
        return pd.DataFrame()
# =====================================================
# 3. COMPONENTE GENÉRICO DE RENDERIZADO
# =====================================================
def render_cubo(titulo, vistas, etiquetas_tabs, tipos_graficos):
    st.markdown(f"<h1>{titulo}</h1>", unsafe_allow_html=True)
    tabs = st.tabs(etiquetas_tabs)
    
    for i, tab in enumerate(tabs):
        with tab:
            df = run_query(f"SELECT * FROM {vistas[i]}")
            
            if df.empty:
                st.info(f"🌑 La vista '{vistas[i]}' está esperando datos de población o corrección en SQL.")
                continue
            
            if tipos_graficos[i] == "line":
                fig = px.line(df, x=df.columns[0], y=df.columns[1], template="plotly_dark", markers=True, color_discrete_sequence=['#00f2ff'])
                st.plotly_chart(fig, use_container_width=True)
                
            elif tipos_graficos[i] == "bar":
                fig = px.bar(df, x=df.columns[0], y=df.columns[1], color=df.columns[0], template="plotly_dark", color_discrete_sequence=px.colors.sequential.Electric)
                st.plotly_chart(fig, use_container_width=True)
                
            elif tipos_graficos[i] == "pie":
                fig = px.pie(df, names=df.columns[0], values=df.columns[1], hole=0.6, template="plotly_dark", color_discrete_sequence=px.colors.qualitative.Pastel)
                st.plotly_chart(fig, use_container_width=True)
                
            elif tipos_graficos[i] == "metric":
                col1, col2 = st.columns([1, 2])
                with col1:
                    label_name = df.columns[0].replace('_', ' ').title()
                    value = df.iloc[0,0]
                    st.metric(label=label_name, value=value)
                with col2:
                    st.dataframe(df, use_container_width=True)

# =====================================================
# 4. SIDEBAR Y NAVEGACIÓN
# =====================================================
st.sidebar.image("https://cdn-icons-png.flaticon.com/512/2983/2983973.png", width=80)
st.sidebar.title("Horizon Stay BI")
st.sidebar.markdown("---")

menu = st.sidebar.selectbox("Selecciona un Cubo OLAP:", [
    "Cubo 1: Financiero", "Cubo 2: Ocupación", "Cubo 3: Servicios",
    "Cubo 4: Logística", "Cubo 5: CRM", "Cubo 6: Marketing",
    "Cubo 7: Eventos", "Cubo 8: Auditoría"
])

# MAPEO DE CUBOS CON LAS CORRECCIONES REALIZADAS
if menu == "Cubo 1: Financiero":
    # Incluye v_rev_metodo_pago (Corregida con JOIN detalle_pago)
    render_cubo("💰 Inteligencia Financiera", 
                ["v_rev_mensual", "v_rev_metodo_pago", "v_rev_ticket_medio", "v_rev_impuestos"], 
                ["📅 Ingresos Mensuales", "💳 Métodos de Pago", "📊 Ticket Promedio", ],
                ["line", "pie", "metric", "bar"])

elif menu == "Cubo 2: Ocupación":
    # Incluye v_occ_tipo y v_occ_piso (Corregidas con alias th, h, dr, r)
    render_cubo("🏨 Gestión de Ocupación", 
                ["v_occ_tipo", "v_occ_piso", "v_occ_estadia"], 
                ["🛏️ Por Tipo Habitacion", "🏢 Por Piso", ],
                ["bar", "bar", "metric"])

elif menu == "Cubo 3: Servicios":
    render_cubo("💎 Upselling & Servicios", 
                ["v_srv_populares", "v_srv_uso_transporte"], 
                ["⭐ Top Servicios", "🚐 Uso Transporte"],
                ["bar", "pie"])

elif menu == "Cubo 4: Logística":
    render_cubo("🗺️ Logística Horizon", 
                ["v_tra_rutas_top", "v_tra_disponibilidad"], 
                ["📍 Rutas Populares", "🚐 Disponibilidad Flota"],
                ["bar", "pie"])

elif menu == "Cubo 5: CRM":
    render_cubo("👥 Fidelización (CRM)", 
                ["v_crm_niveles", "v_crm_retorno"], 
                ["🏆 Distribución VIP", "🔄 Tasa de Retorno"],
                ["bar", "pie"])

elif menu == "Cubo 6: Marketing":
    render_cubo("📈 Impacto de Marketing", 
                ["v_mkt_impacto_dto", "v_mkt_temporadas"], 
                ["🎟️ % Descuento Promedio", "🌦️ Ingreso por Temporada"],
                ["metric", "line"])

elif menu == "Cubo 7: Eventos":
    render_cubo("🎭 Análisis de Eventos", 
                ["v_eve_ingresos", "v_eve_capacidad"], 
                ["💵 Ingreso por Paquete", "👥 Capacidad Media"],
                ["bar", "metric"])

elif menu == "Cubo 8: Auditoría":
    render_cubo("🛡️ Auditoría de Calidad", 
                ["v_aud_cancelaciones", "v_aud_balance"], 
                ["🚫 Estado Reservas", "⚖️ Balance Real"],
                ["pie", "bar"])

# FOOTER
st.sidebar.markdown("---")
st.sidebar.info(f"👤 **Analista:** Adrian\n\n📅 **Fecha:** {datetime.now().strftime('%d/%m/%Y')}")

if st.sidebar.button("♻️ Refrescar Datos"):
    st.cache_resource.clear()
    st.rerun()
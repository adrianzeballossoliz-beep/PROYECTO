import streamlit as st
import pandas as pd
import psycopg2
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

st.set_page_config(
    page_title="Horizon Stay BI",
    page_icon="🏨",
    layout="wide",
    initial_sidebar_state="expanded"
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@300;400;500;600;700&family=Syne:wght@700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Space Grotesk', sans-serif;
    }
    .stApp {
        background: #060910;
    }
    /* SIDEBAR */
    [data-testid="stSidebar"] {
        background: #080c14 !important;
        border-right: 1px solid rgba(0, 200, 255, 0.15);
    }
    [data-testid="stSidebar"] * {
        color: #a0b4c8 !important;
    }
    /* TITULO PRINCIPAL */
    .main-title {
        font-family: 'Syne', sans-serif;
        font-size: 2.6rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00d4ff 0%, #7b2fff 50%, #00ffb3 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0;
        line-height: 1.1;
    }
    .sub-title {
        color: #4a6478;
        font-size: 0.9rem;
        letter-spacing: 0.15em;
        text-transform: uppercase;
        margin-top: 4px;
    }
    /* ENCABEZADO DE CUBO */
    .cubo-header {
        background: linear-gradient(135deg, rgba(0,212,255,0.08), rgba(123,47,255,0.08));
        border: 1px solid rgba(0,212,255,0.2);
        border-radius: 12px;
        padding: 20px 24px;
        margin-bottom: 24px;
    }
    .cubo-title {
        font-family: 'Syne', sans-serif;
        font-size: 1.6rem;
        font-weight: 800;
        color: #00d4ff;
        margin: 0;
    }
    .cubo-desc {
        color: #4a6478;
        font-size: 0.85rem;
        margin-top: 4px;
    }
    /* MÉTRICAS */
    .metric-card {
        background: rgba(10, 18, 30, 0.8);
        border: 1px solid rgba(0, 212, 255, 0.15);
        border-radius: 10px;
        padding: 18px 20px;
        text-align: center;
    }
    .metric-value {
        font-family: 'Syne', sans-serif;
        font-size: 2rem;
        font-weight: 800;
        color: #00d4ff;
    }
    .metric-label {
        font-size: 0.75rem;
        color: #4a6478;
        text-transform: uppercase;
        letter-spacing: 0.1em;
        margin-top: 4px;
    }
    /* SEPARADOR */
    .section-divider {
        border: none;
        border-top: 1px solid rgba(0,212,255,0.1);
        margin: 20px 0;
    }
    /* GRÁFICO LABEL */
    .chart-label {
        font-size: 0.78rem;
        color: #4a6478;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        margin-bottom: 8px;
        padding-left: 4px;
    }
    /* EXPANDER */
    .streamlit-expanderHeader {
        background: rgba(10,18,30,0.6) !important;
        color: #4a6478 !important;
        border: 1px solid rgba(0,212,255,0.1) !important;
        border-radius: 8px !important;
    }
    /* SELECTBOX SIDEBAR */
    .stSelectbox > div > div {
        background: rgba(10,18,30,0.8) !important;
        border: 1px solid rgba(0,212,255,0.2) !important;
        color: #a0b4c8 !important;
    }
    /* BOTÓN */
    .stButton > button {
        background: linear-gradient(135deg, #00d4ff22, #7b2fff22) !important;
        border: 1px solid rgba(0,212,255,0.3) !important;
        color: #00d4ff !important;
        border-radius: 8px !important;
        font-family: 'Space Grotesk', sans-serif !important;
        letter-spacing: 0.05em;
        width: 100%;
    }
    .stButton > button:hover {
        border-color: #00d4ff !important;
        box-shadow: 0 0 12px rgba(0,212,255,0.2) !important;
    }
</style>
""", unsafe_allow_html=True)


PLOTLY_TEMPLATE = dict(
    layout=dict(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(8,12,20,0.6)",
        font=dict(family="Space Grotesk", color="#a0b4c8", size=12),
        title=dict(font=dict(family="Syne", color="#00d4ff", size=15)),
        xaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)", tickcolor="rgba(255,255,255,0.1)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.05)", linecolor="rgba(255,255,255,0.1)", tickcolor="rgba(255,255,255,0.1)"),
        legend=dict(bgcolor="rgba(10,18,30,0.6)", bordercolor="rgba(0,212,255,0.2)", borderwidth=1),
        colorway=["#00d4ff", "#7b2fff", "#00ffb3", "#ff6b6b", "#ffd93d", "#ff9f43", "#a29bfe", "#fd79a8"],
        margin=dict(t=50, b=40, l=40, r=20),
    )
)

@st.cache_resource
def get_connection():
    return psycopg2.connect(
        host="localhost",
        database="postgres",
        user="postgres",
        password="123456",
        port="5432",
    )

def run_query(query):
    try:
        conn = get_connection()
        df = pd.read_sql(query, conn)
        return df
    except Exception as e:
        st.error(f"⚠️ Error de conexión: {e}")
        return pd.DataFrame()


def cubo_header(titulo, descripcion):
    st.markdown(f"""
    <div class="cubo-header">
        <p class="cubo-title">{titulo}</p>
        <p class="cubo-desc">{descripcion}</p>
    </div>
    """, unsafe_allow_html=True)

def chart_label(txt):
    st.markdown(f'<p class="chart-label">{txt}</p>', unsafe_allow_html=True)

#OLAP

# ── CUBO 1: INGRESOS
def cubo_ingresos():
    cubo_header("💰 Inteligencia Financiera", "Análisis de ingresos por categoría, método de pago y periodo")
    df = run_query("SELECT * FROM cubo_ingresos")
    if df.empty:
        st.info("Sin datos disponibles en cubo_ingresos.")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">Bs {df["total_bolivianos"].sum():,.0f}</div><div class="metric-label">Ingreso Total</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{df["cantidad_facturas"].sum():,}</div><div class="metric-label">Facturas Emitidas</div></div>', unsafe_allow_html=True)
    with c3:
        promedio = df["total_bolivianos"].sum() / max(df["cantidad_facturas"].sum(), 1)
        st.markdown(f'<div class="metric-card"><div class="metric-value">Bs {promedio:,.0f}</div><div class="metric-label">Ticket Promedio</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        chart_label("Tendencia mensual de ingresos")
        if "mes_operacion" in df.columns:
            df["mes_operacion"] = pd.to_datetime(df["mes_operacion"])
            fig = px.line(df, x="mes_operacion", y="total_bolivianos",
                          color="categoria_habitacion", markers=True,
                          title="Ingresos por Mes y Categoría")
            fig.update_layout(**PLOTLY_TEMPLATE["layout"])
            fig.update_traces(line=dict(width=2.5))
            st.plotly_chart(fig, use_container_width=True)

    with col2:
        chart_label("Ingresos por método de pago")
        df_metodo = df.groupby("forma_pago")["total_bolivianos"].sum().reset_index()
        fig2 = px.bar(df_metodo, x="forma_pago", y="total_bolivianos",
                      color="forma_pago", title="Total por Forma de Pago")
        fig2.update_layout(**PLOTLY_TEMPLATE["layout"])
        st.plotly_chart(fig2, use_container_width=True)

    chart_label("Distribución de ingresos por categoría de habitación")
    df_cat = df.groupby("categoria_habitacion")["total_bolivianos"].sum().reset_index()
    fig3 = px.pie(df_cat, names="categoria_habitacion", values="total_bolivianos",
                  hole=0.55, title="Participación por Categoría")
    fig3.update_layout(**PLOTLY_TEMPLATE["layout"])
    fig3.update_traces(textfont_color="#ffffff")
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("📋 Ver datos completos"):
        st.dataframe(df, use_container_width=True)


# ── CUBO 2: OCUPACIÓN 
def cubo_ocupacion():
    cubo_header("🏨 Gestión de Ocupación", "Estado actual e histórico de habitaciones por categoría")
    df = run_query("SELECT * FROM cubo_ocupacion")
    if df.empty:
        st.info("Sin datos disponibles en cubo_ocupacion.")
        return

    c1, c2, c3 = st.columns(3)
    ocupadas = df[df["disponibilidad_real"] == "Ocupada Hoy"].shape[0]
    libres = df[df["disponibilidad_real"] == "Libre Hoy"].shape[0]
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{df.shape[0]}</div><div class="metric-label">Total Habitaciones</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#00ffb3">{ocupadas}</div><div class="metric-label">Ocupadas Hoy</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#ff6b6b">{libres}</div><div class="metric-label">Libres Hoy</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        chart_label("Usos históricos por categoría")
        df_cat = df.groupby("categoria")["historial_usos"].sum().reset_index()
        fig = px.bar(df_cat, x="categoria", y="historial_usos",
                     color="categoria", title="Historial de Usos por Tipo")
        fig.update_layout(**PLOTLY_TEMPLATE["layout"])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        chart_label("Disponibilidad real — hoy")
        df_disp = df.groupby("disponibilidad_real").size().reset_index(name="cantidad")
        fig2 = px.pie(df_disp, names="disponibilidad_real", values="cantidad",
                      hole=0.5, title="Ocupada vs Libre (Hoy)",
                      color_discrete_sequence=["#00ffb3", "#ff6b6b"])
        fig2.update_layout(**PLOTLY_TEMPLATE["layout"])
        st.plotly_chart(fig2, use_container_width=True)

    chart_label("Estado actual de cada habitación")
    df_estado = df.groupby(["categoria", "estado_actual"]).size().reset_index(name="cantidad")
    fig3 = px.bar(df_estado, x="categoria", y="cantidad", color="estado_actual",
                  barmode="stack", title="Estados por Categoría")
    fig3.update_layout(**PLOTLY_TEMPLATE["layout"])
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("📋 Ver datos completos"):
        st.dataframe(df, use_container_width=True)


# ── CUBO 3: RRHH
def cubo_rrhh():
    cubo_header("👷 Rendimiento de Personal", "Asistencias, bonos y desempeño por departamento")
    df = run_query("SELECT * FROM cubo_rrhh_rendimiento")
    if df.empty:
        st.info("Sin datos disponibles en cubo_rrhh_rendimiento.")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{df.shape[0]}</div><div class="metric-label">Empleados</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{int(df["total_asistencias"].sum())}</div><div class="metric-label">Asistencias Totales</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">Bs {df["total_bonos_pagados"].sum():,.0f}</div><div class="metric-label">Bonos Pagados</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        chart_label("Asistencias por departamento")
        df_depto = df.groupby("departamento")["total_asistencias"].sum().reset_index()
        fig = px.bar(df_depto, x="departamento", y="total_asistencias",
                     color="departamento", title="Asistencias por Depto.")
        fig.update_layout(**PLOTLY_TEMPLATE["layout"])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        chart_label("Bonos por empleado")
        df_bono = df[df["total_bonos_pagados"] > 0].sort_values("total_bonos_pagados", ascending=True)
        fig2 = px.bar(df_bono, x="total_bonos_pagados", y="nombre_empleado",
                      orientation="h", color="total_bonos_pagados",
                      color_continuous_scale=["#7b2fff", "#00d4ff"],
                      title="Bonos por Empleado")
        fig2.update_layout(**PLOTLY_TEMPLATE["layout"])
        st.plotly_chart(fig2, use_container_width=True)

    chart_label("Distribución de asistencias por cargo")
    df_cargo = df.groupby("cargo")["total_asistencias"].sum().reset_index()
    fig3 = px.pie(df_cargo, names="cargo", values="total_asistencias",
                  hole=0.5, title="Asistencias por Cargo")
    fig3.update_layout(**PLOTLY_TEMPLATE["layout"])
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("📋 Ver datos completos"):
        st.dataframe(df, use_container_width=True)


# ── CUBO 4: FIDELIZACIÓN 
def cubo_fidelidad():
    cubo_header("💎 Fidelización y Consumo", "Servicios consumidos por nivel de fidelidad de clientes")
    df = run_query("SELECT * FROM cubo_fidelidad_consumo")
    if df.empty:
        st.info("Sin datos disponibles en cubo_fidelidad_consumo.")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{int(df["unidades_vendidas"].sum())}</div><div class="metric-label">Servicios Vendidos</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">Bs {df["ingresos_totales_bs"].sum():,.0f}</div><div class="metric-label">Ingresos por Servicios</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{df["servicio_consumido"].nunique()}</div><div class="metric-label">Servicios Distintos</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        chart_label("Ingresos por nivel de fidelidad")
        df_nivel = df.groupby("categoria_fidelidad")["ingresos_totales_bs"].sum().reset_index()
        fig = px.pie(df_nivel, names="categoria_fidelidad", values="ingresos_totales_bs",
                     hole=0.5, title="Ingresos por Nivel de Cliente")
        fig.update_layout(**PLOTLY_TEMPLATE["layout"])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        chart_label("Servicios más consumidos")
        df_serv = df.groupby("servicio_consumido")["unidades_vendidas"].sum().reset_index().sort_values("unidades_vendidas", ascending=True)
        fig2 = px.bar(df_serv, x="unidades_vendidas", y="servicio_consumido",
                      orientation="h", color="unidades_vendidas",
                      color_continuous_scale=["#7b2fff", "#00ffb3"],
                      title="Top Servicios por Unidades")
        fig2.update_layout(**PLOTLY_TEMPLATE["layout"])
        st.plotly_chart(fig2, use_container_width=True)

    chart_label("Ingresos por categoría de servicio vs nivel de cliente")
    df_cross = df.groupby(["categoria_fidelidad", "categoria_servicio"])["ingresos_totales_bs"].sum().reset_index()
    fig3 = px.bar(df_cross, x="categoria_fidelidad", y="ingresos_totales_bs",
                  color="categoria_servicio", barmode="group",
                  title="Consumo por Nivel y Categoría de Servicio")
    fig3.update_layout(**PLOTLY_TEMPLATE["layout"])
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("📋 Ver datos completos"):
        st.dataframe(df, use_container_width=True)


# ── CUBO 5: MANTENIMIENTO 
def cubo_mantenimiento():
    cubo_header("🛠️ Gastos de Mantenimiento", "Intervenciones y costos de mantenimiento por categoría de habitación")
    df = run_query("SELECT * FROM cubo_mantenimiento_gastos")
    if df.empty:
        st.info("Sin datos disponibles en cubo_mantenimiento_gastos.")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{int(df["total_intervenciones"].sum())}</div><div class="metric-label">Intervenciones</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">Bs {df["gasto_total_mantenimiento_bs"].sum():,.0f}</div><div class="metric-label">Gasto Total</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">Bs {df["costo_promedio_reparacion"].mean():,.0f}</div><div class="metric-label">Costo Promedio</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        chart_label("Gasto total por categoría")
        fig = px.bar(df, x="categoria_habitacion", y="gasto_total_mantenimiento_bs",
                     color="categoria_habitacion", title="Gasto Total por Tipo de Habitación")
        fig.update_layout(**PLOTLY_TEMPLATE["layout"])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        chart_label("Número de intervenciones por categoría")
        fig2 = px.bar(df, x="categoria_habitacion", y="total_intervenciones",
                      color="categoria_habitacion",
                      color_discrete_sequence=["#7b2fff","#00ffb3","#ff6b6b","#ffd93d","#00d4ff"],
                      title="Intervenciones por Categoría")
        fig2.update_layout(**PLOTLY_TEMPLATE["layout"])
        st.plotly_chart(fig2, use_container_width=True)

    chart_label("Costo promedio de reparación por categoría")
    fig3 = px.scatter(df, x="categoria_habitacion", y="costo_promedio_reparacion",
                      size="total_intervenciones", color="categoria_habitacion",
                      title="Costo Promedio vs Frecuencia (tamaño = intervenciones)")
    fig3.update_layout(**PLOTLY_TEMPLATE["layout"])
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("📋 Ver datos completos"):
        st.dataframe(df, use_container_width=True)


# ── CUBO 6: SATISFACCIÓN 
def cubo_satisfaccion():
    cubo_header("⭐ Calidad del Servicio", "Puntuaciones de encuestas de satisfacción por categoría de habitación")
    df = run_query("SELECT * FROM cubo_satisfaccion_cliente")
    if df.empty:
        st.info("Sin datos disponibles en cubo_satisfaccion_cliente.")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{int(df["cantidad_encuestas"].sum())}</div><div class="metric-label">Encuestas Totales</div></div>', unsafe_allow_html=True)
    with c2:
        promedio_global = df["promedio_estrellas"].mean()
        st.markdown(f'<div class="metric-card"><div class="metric-value">{promedio_global:.2f} ⭐</div><div class="metric-label">Promedio Global</div></div>', unsafe_allow_html=True)
    with c3:
        excelentes = df[df["estado_opinion"] == "Excelente"].shape[0]
        st.markdown(f'<div class="metric-card"><div class="metric-value" style="color:#00ffb3">{excelentes}</div><div class="metric-label">Categorías Excelentes</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)

    color_map = {"Excelente": "#00ffb3", "Satisfactorio": "#ffd93d", "Crítico - Revisar": "#ff6b6b"}
    col1, col2 = st.columns(2)

    with col1:
        chart_label("Puntuación promedio por categoría")
        fig = px.bar(df, x="categoria", y="promedio_estrellas",
                     color="estado_opinion", color_discrete_map=color_map,
                     title="Promedio de Estrellas por Tipo de Habitación",
                     range_y=[0, 5])
        fig.update_layout(**PLOTLY_TEMPLATE["layout"])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        chart_label("Cantidad de encuestas por categoría")
        fig2 = px.pie(df, names="categoria", values="cantidad_encuestas",
                      hole=0.5, title="Distribución de Encuestas")
        fig2.update_layout(**PLOTLY_TEMPLATE["layout"])
        st.plotly_chart(fig2, use_container_width=True)

    chart_label("Estado de opinión por categoría")
    fig3 = go.Figure()
    for _, row in df.iterrows():
        color = color_map.get(row["estado_opinion"], "#00d4ff")
        fig3.add_trace(go.Indicator(
            mode="gauge+number",
            value=float(row["promedio_estrellas"]),
            title={"text": row["categoria"], "font": {"size": 12, "color": "#a0b4c8"}},
            gauge={
                "axis": {"range": [0, 5], "tickcolor": "#a0b4c8"},
                "bar": {"color": color},
                "bgcolor": "rgba(10,18,30,0.8)",
                "bordercolor": "rgba(0,212,255,0.2)",
            },
            domain={"row": 0, "column": list(df["categoria"]).index(row["categoria"])}
        ))
    fig3.update_layout(
        grid={"rows": 1, "columns": len(df)},
        title=dict(text="Medidor de Satisfacción por Categoría", font=dict(color="#00d4ff", size=14)),
        **{k: v for k, v in PLOTLY_TEMPLATE["layout"].items() if k not in ["xaxis","yaxis"]}
    )
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("📋 Ver datos completos"):
        st.dataframe(df, use_container_width=True)


# ── CUBO 7: NÓMINA 
def cubo_nomina():
    cubo_header("💵 Análisis de Nómina", "Distribución salarial por departamento y cargo")
    df = run_query("""
        SELECT 
            d.nombre_depto AS departamento,
            pt.nombre_puesto AS cargo,
            e.nombre AS empleado,
            n.salario_neto,
            n.fecha_pago
        FROM nomina n
        JOIN empleado e ON n.id_empleado = e.id_empleado
        JOIN puesto_trabajo pt ON e.id_puesto = pt.id_puesto
        JOIN departamento d ON pt.id_depto = d.id_depto
    """)
    if df.empty:
        st.info("Sin datos disponibles en nómina.")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">Bs {df["salario_neto"].sum():,.0f}</div><div class="metric-label">Masa Salarial Total</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">Bs {df["salario_neto"].mean():,.0f}</div><div class="metric-label">Salario Promedio</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">Bs {df["salario_neto"].max():,.0f}</div><div class="metric-label">Salario Más Alto</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        chart_label("Masa salarial por departamento")
        df_depto = df.groupby("departamento")["salario_neto"].sum().reset_index()
        fig = px.bar(df_depto, x="departamento", y="salario_neto",
                     color="departamento", title="Costo Salarial por Depto.")
        fig.update_layout(**PLOTLY_TEMPLATE["layout"])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        chart_label("Distribución salarial por cargo")
        fig2 = px.pie(df, names="cargo", values="salario_neto",
                      hole=0.5, title="Participación por Cargo")
        fig2.update_layout(**PLOTLY_TEMPLATE["layout"])
        st.plotly_chart(fig2, use_container_width=True)

    chart_label("Salario individual por empleado")
    df_sorted = df.sort_values("salario_neto", ascending=True)
    fig3 = px.bar(df_sorted, x="salario_neto", y="empleado",
                  orientation="h", color="departamento",
                  title="Salario Neto por Empleado")
    fig3.update_layout(**PLOTLY_TEMPLATE["layout"])
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("📋 Ver datos completos"):
        st.dataframe(df, use_container_width=True)


# ── CUBO 8: AUDITORÍA 
def cubo_auditoria():
    cubo_header("🛡️ Seguridad del Sistema", "Trazabilidad de operaciones por usuario, módulo y tipo de acción")
    df = run_query("SELECT * FROM cubo_auditoria_seguridad")
    if df.empty:
        st.info("Sin datos disponibles en cubo_auditoria_seguridad.")
        return

    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{int(df["total_movimientos"].sum())}</div><div class="metric-label">Movimientos Totales</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{df["nombre_usuario"].nunique()}</div><div class="metric-label">Usuarios Activos</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-value">{df["modulo_editado"].nunique()}</div><div class="metric-label">Módulos Afectados</div></div>', unsafe_allow_html=True)

    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        chart_label("Movimientos por tipo de operación")
        df_op = df.groupby("tipo_operacion")["total_movimientos"].sum().reset_index()
        color_op = {"INSERT": "#00ffb3", "UPDATE": "#ffd93d", "DELETE": "#ff6b6b"}
        fig = px.bar(df_op, x="tipo_operacion", y="total_movimientos",
                     color="tipo_operacion", color_discrete_map=color_op,
                     title="INSERT / UPDATE / DELETE")
        fig.update_layout(**PLOTLY_TEMPLATE["layout"])
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        chart_label("Actividad por usuario")
        df_user = df.groupby("nombre_usuario")["total_movimientos"].sum().reset_index()
        fig2 = px.pie(df_user, names="nombre_usuario", values="total_movimientos",
                      hole=0.5, title="Operaciones por Empleado")
        fig2.update_layout(**PLOTLY_TEMPLATE["layout"])
        st.plotly_chart(fig2, use_container_width=True)

    chart_label("Mapa de actividad — usuario × módulo")
    df_heat = df.pivot_table(index="nombre_usuario", columns="modulo_editado",
                              values="total_movimientos", fill_value=0)
    fig3 = px.imshow(df_heat, text_auto=True,
                     color_continuous_scale=["#060910", "#7b2fff", "#00d4ff"],
                     title="Heatmap de Actividad (usuario × tabla)")
    fig3.update_layout(**PLOTLY_TEMPLATE["layout"])
    st.plotly_chart(fig3, use_container_width=True)

    with st.expander("📋 Ver datos completos"):
        st.dataframe(df, use_container_width=True)

with st.sidebar:
    st.markdown("""
    <div style="padding:16px 0 8px 0">
        <p style="font-family:'Syne',sans-serif;font-size:1.3rem;font-weight:800;
                  background:linear-gradient(135deg,#00d4ff,#7b2fff);
                  -webkit-background-clip:text;-webkit-text-fill-color:transparent;
                  margin:0">Horizon Stay BI</p>
        <p style="color:#2a3a4a;font-size:0.75rem;letter-spacing:0.1em;
                  text-transform:uppercase;margin:2px 0 0 0">Hotel Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    cubos = {
        "💰  Financiero":       "cubo1",
        "🏨  Ocupación":        "cubo2",
        "👷  RRHH":             "cubo3",
        "💎  Fidelización":     "cubo4",
        "🛠️  Mantenimiento":   "cubo5",
        "💵  Nómina":           "cubo7",
        "🛡️  Auditoría":       "cubo8",
    }
    seleccion = st.selectbox("Módulo de análisis", list(cubos.keys()))
    st.markdown("---")

    if st.button("♻️  Refrescar datos"):
        st.cache_resource.clear()
        st.rerun()

    st.markdown("---")
    st.markdown("""
    <div style="padding:8px 0">
        <p style="color:#2a3a4a;font-size:0.72rem;text-transform:uppercase;
                  letter-spacing:0.1em;margin:0 0 6px 0">Sesión activa</p>
        <p style="color:#4a6478;font-size:0.82rem;margin:0">👤 </p>
        <p style="color:#4a6478;font-size:0.82rem;margin:2px 0 0 0">📚 3er Semestre · Ciencia de Datos</p>
        <p style="color:#2a3a4a;font-size:0.75rem;margin:8px 0 0 0">
    """ + datetime.now().strftime("%d %b %Y · %H:%M") + """
        </p>
    </div>
    """, unsafe_allow_html=True)


st.markdown("""
<div style="margin-bottom:28px">
    <p class="main-title">🏨 Horizon Stay BI</p>
    <p class="sub-title">Business Intelligence Platform · Análisis Multidimensional</p>
</div>
""", unsafe_allow_html=True)

dispatch = {
    "cubo1": cubo_ingresos,
    "cubo2": cubo_ocupacion,
    "cubo3": cubo_rrhh,
    "cubo4": cubo_fidelidad,
    "cubo5": cubo_mantenimiento,
    "cubo6": cubo_satisfaccion,
    "cubo7": cubo_nomina,
    "cubo8": cubo_auditoria,
}
dispatch[cubos[seleccion]]()
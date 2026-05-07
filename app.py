import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from cv_processor import process_all_candidates, extract_skills
from sample_data import SAMPLE_CVS, SAMPLE_JOBS

st.set_page_config(
    page_title="Datalynx — Selección con IA",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    /* Encabezado principal */
    .main-header {
        background: linear-gradient(135deg, #1a1f3a 0%, #2d3561 100%);
        padding: 1.5rem 2rem;
        border-radius: 12px;
        margin-bottom: 1.5rem;
        color: white;
    }
    .main-header h1 { margin: 0; font-size: 2rem; color: white; }
    .main-header p  { margin: 0.3rem 0 0; opacity: 0.8; font-size: 0.95rem; }

    /* Tarjetas de métricas */
    .metric-card {
        background: white;
        border: 1px solid #e8ecf0;
        border-radius: 10px;
        padding: 1rem 1.2rem;
        text-align: center;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    }
    .metric-card .value { font-size: 2rem; font-weight: 700; color: #2d3561; }
    .metric-card .label { font-size: 0.8rem; color: #666; margin-top: 0.2rem; }

    /* Badges de habilidades */
    .skill-match   { background:#d4edda; color:#155724; padding:3px 10px; border-radius:20px;
                     font-size:0.78rem; margin:2px; display:inline-block; }
    .skill-missing { background:#f8d7da; color:#721c24; padding:3px 10px; border-radius:20px;
                     font-size:0.78rem; margin:2px; display:inline-block; }
    .skill-extra   { background:#cce5ff; color:#004085; padding:3px 10px; border-radius:20px;
                     font-size:0.78rem; margin:2px; display:inline-block; }

    /* Ranking top 3 */
    .rank-1 { border-left: 5px solid #FFD700; }
    .rank-2 { border-left: 5px solid #C0C0C0; }
    .rank-3 { border-left: 5px solid #CD7F32; }

    /* Ocultar botón de menú de Streamlit */
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }
</style>
""", unsafe_allow_html=True)


# ── Funciones auxiliares ─────────────────────────────────────

def score_color(score: float) -> str:
    """Devuelve un emoji de color según la puntuación."""
    if score >= 7:
        return "🟢"
    elif score >= 5:
        return "🟡"
    else:
        return "🔴"


def render_skills_badges(skills: list, css_class: str) -> str:
    """Genera HTML con badges de habilidades."""
    if not skills:
        return "<em style='color:#999'>Ninguna</em>"
    return " ".join(f'<span class="{css_class}">{s}</span>' for s in skills)


def radar_chart(scores: dict, candidato_id: str) -> go.Figure:
    """Genera un gráfico de radar con el desglose de puntuación."""
    categories = ["Habilidades", "Similitud Semántica", "Experiencia"]
    values = [
        scores["score_habilidades"],
        scores["score_semantico"],
        scores["score_experiencia"],
    ]

    fig = go.Figure(go.Scatterpolar(
        r=values + [values[0]],
        theta=categories + [categories[0]],
        fill="toself",
        fillcolor="rgba(45,53,97,0.2)",
        line=dict(color="#2d3561", width=2),
        name=candidato_id,
    ))
    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 10], tickfont_size=10),
        ),
        showlegend=False,
        margin=dict(t=20, b=20, l=30, r=30),
        height=280,
    )
    return fig


if "resultados" not in st.session_state:
    st.session_state.resultados = None
if "modo_admin" not in st.session_state:
    st.session_state.modo_admin = False
if "candidatos_personalizados" not in st.session_state:
    st.session_state.candidatos_personalizados = []


# ── Encabezado ───────────────────────────────────────────────
st.markdown("""
<div class="main-header">
    <h1>🔍 Datalynx</h1>
    <p>Plataforma de selección de personal con Inteligencia Artificial · Análisis objetivo y sin sesgos</p>
</div>
""", unsafe_allow_html=True)


with st.sidebar:
    st.image("https://via.placeholder.com/200x60/2d3561/ffffff?text=DATALYNX", width=200)
    st.markdown("---")
    st.header("⚙️ Configurar Oferta")

    modo_oferta = st.radio(
        "Modo de oferta:",
        ["📋 Oferta de demo", "✏️ Oferta personalizada"],
        horizontal=False,
    )

    if modo_oferta == "📋 Oferta de demo":
        oferta_seleccionada = st.selectbox(
            "Selecciona una oferta:",
            options=SAMPLE_JOBS,
            format_func=lambda j: j["titulo"],
        )
        titulo_oferta = oferta_seleccionada["titulo"]
        descripcion_oferta = oferta_seleccionada["descripcion"].strip()
        habilidades_requeridas = oferta_seleccionada["habilidades_requeridas"]
    else:
        titulo_oferta = st.text_input("Título del puesto:", "Data Scientist")
        descripcion_oferta = st.text_area(
            "Descripción del puesto:",
            "Buscamos un Data Scientist con experiencia en Python, Machine Learning y SQL...",
            height=120,
        )
        skills_input = st.text_input(
            "Habilidades requeridas (separadas por comas):",
            "Python, Machine Learning, SQL, Pandas",
        )
        habilidades_requeridas = [s.strip() for s in skills_input.split(",") if s.strip()]

    st.markdown("---")

    st.session_state.modo_admin = st.toggle(
        "👁️ Modo administrador (ver nombres reales)",
        value=False,
        help="Activa esta opción para ver los nombres reales de los candidatos. "
             "Normalmente los reclutadores solo ven los IDs anonimizados.",
    )

    st.markdown("---")

    st.subheader("👥 Candidatos")
    usar_demo = st.checkbox("Usar candidatos de demo", value=True)

    candidatos_a_analizar = SAMPLE_CVS.copy() if usar_demo else []

    # Subir CVs en PDF
    with st.expander("➕ Subir CVs en PDF"):
        pdfs = st.file_uploader(
            "Selecciona uno o varios CVs:",
            type=["pdf"],
            accept_multiple_files=True,
            help="Puedes subir varios PDFs a la vez. El texto se extrae automáticamente.",
        )

        
        import pdfplumber
        nombres_actuales = {
            f.name.replace(".pdf", "").replace("_", " ").replace("-", " ").title()
            for f in (pdfs or [])
        }
        st.session_state.candidatos_personalizados = [
            c for c in st.session_state.candidatos_personalizados
            if c.get("nombre") in nombres_actuales
        ]
        # Añadir los PDFs nuevos que aún no están procesados
        nombres_ya_cargados = {c.get("nombre") for c in st.session_state.candidatos_personalizados}
        for pdf_file in (pdfs or []):
            nombre_pdf = pdf_file.name.replace(".pdf", "").replace("_", " ").replace("-", " ").title()
            if nombre_pdf in nombres_ya_cargados:
                continue
            try:
                with pdfplumber.open(pdf_file) as pdf:
                    texto = "\n".join(page.extract_text() or "" for page in pdf.pages)
                if texto.strip():
                    st.session_state.candidatos_personalizados.append({
                        "id": len(SAMPLE_CVS) + len(st.session_state.candidatos_personalizados) + 1,
                        "nombre": nombre_pdf,
                        "texto_cv": texto,
                    })
                    st.success(f"✅ {pdf_file.name} cargado")
                else:
                    st.warning(f"⚠️ {pdf_file.name} está escaneado (imagen). No se pudo extraer texto.")
            except Exception as e:
                st.error(f"❌ Error al leer {pdf_file.name}: {e}")

    if st.session_state.candidatos_personalizados:
        candidatos_a_analizar += st.session_state.candidatos_personalizados
        if st.button("🗑️ Limpiar todos los PDFs"):
            st.session_state.candidatos_personalizados = []
            st.rerun()

    st.markdown(f"**Candidatos a analizar: {len(candidatos_a_analizar)}**")
    st.markdown("---")

    analizar = st.button(
        "🚀 Analizar candidatos",
        type="primary",
        use_container_width=True,
        disabled=len(candidatos_a_analizar) == 0,
    )


if analizar:
    with st.spinner("⏳ Procesando CVs con IA... Extrayendo habilidades, calculando similitud semántica y anonimizando datos..."):
        df = process_all_candidates(
            candidatos_a_analizar,
            descripcion_oferta,
            habilidades_requeridas,
        )
        st.session_state.resultados = df
        st.session_state.oferta_titulo = titulo_oferta
        st.session_state.habilidades_req = habilidades_requeridas

if st.session_state.resultados is not None:
    df = st.session_state.resultados
    oferta_titulo = st.session_state.get("oferta_titulo", titulo_oferta)
    habilidades_req = st.session_state.get("habilidades_req", habilidades_requeridas)

    st.markdown(f"### 📊 Resultados para: *{oferta_titulo}*")

    # ── KPIs de resumen ──────────────────────────────────────
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("👥 Candidatos analizados", len(df))
    with col2:
        st.metric("⭐ Puntuación media", f"{df['puntuacion'].mean():.2f}/10")
    with col3:
        aptos = len(df[df["puntuacion"] >= 6])
        st.metric("✅ Candidatos aptos (≥6)", aptos)
    with col4:
        top_score = df["puntuacion"].max()
        st.metric("🏆 Mejor puntuación", f"{top_score}/10")

    st.markdown("---")

    tab1, tab2, tab3 = st.tabs([
        "🏆 Ranking de candidatos",
        "🔎 Análisis individual",
        "📈 Estadísticas",
    ])

    with tab1:
        st.subheader("Ranking de candidatos (mayor a menor puntuación)")

        mostrar_nombre = st.session_state.modo_admin

        for i, row in df.iterrows():
            rank_class = f"rank-{i}" if i <= 3 else ""
            emoji_rank = ["🥇", "🥈", "🥉"][i - 1] if i <= 3 else f"#{i}"
            nombre_display = row["nombre_real"] if mostrar_nombre else row["candidato_id"]

            with st.container():
                col_rank, col_info, col_score, col_bars = st.columns([0.5, 3, 1, 2])

                with col_rank:
                    st.markdown(f"<h2 style='text-align:center;margin:0'>{emoji_rank}</h2>", unsafe_allow_html=True)

                with col_info:
                    st.markdown(f"**{nombre_display}**")
                    st.markdown(
                        f"🎯 Skills coincidentes: {render_skills_badges(row['habilidades_coincidentes'], 'skill-match')}",
                        unsafe_allow_html=True,
                    )
                    if row["habilidades_faltantes"]:
                        st.markdown(
                            f"❌ Skills faltantes: {render_skills_badges(row['habilidades_faltantes'], 'skill-missing')}",
                            unsafe_allow_html=True,
                        )

                with col_score:
                    color = score_color(row["puntuacion"])
                    st.markdown(
                        f"<div style='text-align:center'>"
                        f"<span style='font-size:2rem;font-weight:700;color:#2d3561'>{row['puntuacion']}</span>"
                        f"<span style='color:#999'>/10</span><br>{color}</div>",
                        unsafe_allow_html=True,
                    )
                    st.caption(f"🗓️ {row['anos_experiencia']} años exp.")

                with col_bars:
                    # Mini barras de desglose
                    for label, val_key in [
                        ("Skills", "score_habilidades"),
                        ("Semántica", "score_semantico"),
                        ("Experiencia", "score_experiencia"),
                    ]:
                        val = row[val_key]
                        st.progress(val / 10, text=f"{label}: {val:.1f}/10")

            st.markdown("---")

    with tab2:
        st.subheader("Análisis detallado de un candidato")

        nombres_display = (
            [f"{row['nombre_real']} ({row['candidato_id']})" for _, row in df.iterrows()]
            if st.session_state.modo_admin
            else list(df["candidato_id"])
        )
        seleccion = st.selectbox("Selecciona un candidato:", nombres_display)

        # Buscar la fila seleccionada
        idx_sel = nombres_display.index(seleccion)
        candidato = df.iloc[idx_sel]

        col_left, col_right = st.columns([2, 1])

        with col_left:
            nombre_show = candidato["nombre_real"] if st.session_state.modo_admin else candidato["candidato_id"]
            st.markdown(f"### {nombre_show}")
            st.markdown(f"**Puntuación total:** {score_color(candidato['puntuacion'])} **{candidato['puntuacion']}/10**")
            st.markdown(f"**Años de experiencia:** {candidato['anos_experiencia']}")

            st.markdown("#### ✅ Habilidades que cumple:")
            st.markdown(
                render_skills_badges(candidato["habilidades_coincidentes"], "skill-match")
                or "<em>Ninguna</em>",
                unsafe_allow_html=True,
            )

            st.markdown("#### ❌ Habilidades que le faltan:")
            st.markdown(
                render_skills_badges(candidato["habilidades_faltantes"], "skill-missing")
                or "<em>Ninguna — cumple todos los requisitos</em>",
                unsafe_allow_html=True,
            )

            otras = [s for s in candidato["habilidades_encontradas"]
                     if s not in candidato["habilidades_coincidentes"]]
            if otras:
                st.markdown("#### 💡 Otras habilidades detectadas:")
                st.markdown(render_skills_badges(otras, "skill-extra"), unsafe_allow_html=True)

        with col_right:
            st.markdown("#### Desglose por criterio")
            fig = radar_chart(candidato, candidato["candidato_id"])
            st.plotly_chart(fig, use_container_width=True)

        # Texto del CV (anonimizado o real según modo)
        with st.expander("📄 Ver texto del CV"):
            if st.session_state.modo_admin:
                opcion_texto = st.radio("Mostrar:", ["Anonimizado", "Original"], horizontal=True)
                texto = candidato["texto_original"] if opcion_texto == "Original" else candidato["texto_anonimizado"]
            else:
                texto = candidato["texto_anonimizado"]
            st.text_area("Contenido del CV:", texto, height=250, disabled=True)

    with tab3:
        st.subheader("Estadísticas del proceso de selección")

        col_a, col_b = st.columns(2)

        with col_a:
            fig_hist = px.histogram(
                df,
                x="puntuacion",
                nbins=10,
                title="Distribución de puntuaciones",
                color_discrete_sequence=["#2d3561"],
                labels={"puntuacion": "Puntuación (0-10)", "count": "Candidatos"},
            )
            fig_hist.add_vline(x=6, line_dash="dash", line_color="green",
                               annotation_text="Mínimo apto (6)")
            fig_hist.update_layout(showlegend=False, height=300)
            st.plotly_chart(fig_hist, use_container_width=True)

        with col_b:
            df_plot = df.copy()
            df_plot["nombre_display"] = (
                df_plot["nombre_real"] if st.session_state.modo_admin else df_plot["candidato_id"]
            )
            fig_bar = px.bar(
                df_plot,
                x="nombre_display",
                y=["score_habilidades", "score_semantico", "score_experiencia"],
                title="Desglose por criterio",
                labels={"value": "Puntuación", "variable": "Criterio", "nombre_display": "Candidato"},
                barmode="group",
                color_discrete_map={
                    "score_habilidades": "#2d3561",
                    "score_semantico": "#5b6abf",
                    "score_experiencia": "#a8b0e8",
                },
                height=300,
            )
            fig_bar.update_layout(legend=dict(orientation="h", y=-0.3))
            st.plotly_chart(fig_bar, use_container_width=True)

        st.subheader("Mapa de cobertura de habilidades requeridas")
        habilidades_req_local = habilidades_req

        if habilidades_req_local:
            heatmap_data = []
            for _, row in df.iterrows():
                nombre_display = row["nombre_real"] if st.session_state.modo_admin else row["candidato_id"]
                cv_skills_norm = [s.lower() for s in row["habilidades_encontradas"]]
                fila = {"Candidato": nombre_display}
                for skill in habilidades_req_local:
                    fila[skill] = 1 if skill.lower() in cv_skills_norm else 0
                heatmap_data.append(fila)

            df_heat = pd.DataFrame(heatmap_data).set_index("Candidato")
            fig_heat = px.imshow(
                df_heat,
                color_continuous_scale=["#f8d7da", "#d4edda"],
                title="Verde = tiene la habilidad | Rojo = le falta",
                aspect="auto",
                labels=dict(color="Tiene skill"),
            )
            fig_heat.update_coloraxes(showscale=False)
            fig_heat.update_layout(height=250 + len(df) * 20)
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.info("Define habilidades requeridas en la barra lateral para ver este mapa.")

        # Tabla de datos completa
        with st.expander("📋 Ver tabla de datos completa"):
            cols_mostrar = [
                "candidato_id", "puntuacion", "anos_experiencia",
                "score_habilidades", "score_semantico", "score_experiencia",
            ]
            if st.session_state.modo_admin:
                cols_mostrar = ["nombre_real"] + cols_mostrar
            st.dataframe(df[cols_mostrar], use_container_width=True)

else:
    st.info("👈 Configura la oferta en la barra lateral y pulsa **Analizar candidatos** para comenzar.")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
        ### 🤖 Motor de IA
        - Extracción de habilidades con **spaCy**
        - Similitud semántica con **TF-IDF**
        - Clasificación con **Scikit-Learn**
        """)
    with col2:
        st.markdown("""
        ### 🔒 Privacidad (RGPD)
        - Eliminación automática de nombres
        - Ocultación de emails y teléfonos
        - Proceso sin sesgo por edad o género
        """)
    with col3:
        st.markdown("""
        ### 📊 Dashboard
        - Ranking por puntuación objetiva
        - Análisis visual de brechas de habilidades
        - Estadísticas del proceso completo
        """)
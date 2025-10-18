
import io
import sys
import math
import numpy as np
import pandas as pd
import streamlit as st
import seaborn as sns
import matplotlib.pyplot as plt
from typing import Optional

# --- Configuración de la Página de Streamlit ---
st.set_page_config(
    page_title="Análisis Segmentado de Juegos Online",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Paleta de colores de Seaborn
COLOR_PALETTE = 'rocket'

# Configuración inicial de estilo
sns.set_theme(style="darkgrid", palette=COLOR_PALETTE)

# --- 1. Carga de Datos y Preprocesamiento ---
@st.cache_data
def load_data(file_path):
    """Carga los datos y realiza el preprocesamiento necesario."""
    try:
        df = pd.read_csv(file_path)
        # Asegurar que Gender y GameGenre sean categóricas
        df['Gender'] = df['Gender'].astype('category')
        df['GameGenre'] = df['GameGenre'].astype('category')
        return df
    except FileNotFoundError:
        st.error(f"Error: No se encontró el archivo {file_path}. Asegúrate de que esté en el mismo directorio.")
        return pd.DataFrame()

df = load_data("online_gaming_insights.csv")

if df.empty:
    st.stop()

# --- 2. Barra Lateral Interactiva y Filtros ---
st.sidebar.title("🛠️ Opciones de Filtrado")

# Selector de modo
analysis_mode = st.sidebar.radio(
    "Selecciona el modo de análisis:",
    ("Vista General", "Análisis Filtrado")
)

st.sidebar.markdown("---")

# Variables de filtro
gender_filter = None
age_filter = None
filtered_df = df.copy()

# Si está en modo filtrado, mostrar opciones
if analysis_mode == "Análisis Filtrado":
    st.sidebar.subheader("Filtros Disponibles")
    
    # Filtro por Género
    gender_filter = st.sidebar.selectbox(
        "Selecciona Género:",
        options=['Todos', 'Male', 'Female'],
        index=0
    )
    
    # Filtro por Rango de Edad
    st.sidebar.markdown("**Rango de Edad:**")
    min_age_data, max_age_data = int(df['Age'].min()), int(df['Age'].max())
    age_filter = st.sidebar.slider(
        "Edad:",
        min_value=min_age_data,
        max_value=max_age_data,
        value=(min_age_data, max_age_data),
        step=1
    )
    
    # Aplicar filtros
    if gender_filter != 'Todos':
        filtered_df = filtered_df[filtered_df['Gender'] == gender_filter]
    
    filtered_df = filtered_df[
        (filtered_df['Age'] >= age_filter[0]) & 
        (filtered_df['Age'] <= age_filter[1])
    ]

# --- 3. Vista General ---
if analysis_mode == "Vista General":
    st.title("🎮 Dashboard de Insights de Juegos Online")
    st.markdown("---")

    # --- KPI's ---
    st.header("1. Indicadores Clave de Rendimiento (KPIs)")
    col1, col2, col3, col4 = st.columns(4)

    total_players = len(df)
    avg_play_time = df['PlayTimeHours'].mean()
    conversion_rate = (df['InGamePurchases'] > 0).sum() / total_players * 100
    avg_level = df['PlayerLevel'].mean()

    col1.metric("Total de Jugadores", f"{total_players:,}")
    col2.metric("Promedio Horas de Juego", f"{avg_play_time:,.2f} hrs")
    col3.metric("Tasa de Compra", f"{conversion_rate:,.2f}%")
    col4.metric("Nivel Promedio de Jugador", f"{avg_level:,.0f}")
    
    st.markdown("---")

    # --- Fragmento del DataFrame ---
    st.header("2. Fragmento de Datos (Muestra)")
    st.dataframe(df.drop(columns=['PlayerID']).head(10), use_container_width=True)
    
    st.markdown("---")
    
    # --- Distribuciones Globales ---
    st.header("3. Distribuciones Globales")
    
    # Fila 1: Edades y Género de Videojuego
    col_age, col_genre = st.columns(2)

    with col_age:
        st.subheader("Distribución de Jugadores por Edad")
        fig_age, ax_age = plt.subplots(figsize=(10, 6))
        sns.histplot(df['Age'], kde=True, bins=20, ax=ax_age, color=sns.color_palette(COLOR_PALETTE)[0])
        ax_age.set_xlabel("Edad", fontsize=12)
        ax_age.set_ylabel("Frecuencia", fontsize=12)
        st.pyplot(fig_age)

    with col_genre:
        st.subheader("Distribución por Género de Videojuego")
        fig_g, ax_g = plt.subplots(figsize=(10, 6))
        sns.countplot(
            data=df, 
            y='GameGenre', 
            order=df['GameGenre'].value_counts().index, 
            palette=COLOR_PALETTE,
            ax=ax_g
        )
        ax_g.set_xlabel("Frecuencia", fontsize=12)
        ax_g.set_ylabel("Género de Juego", fontsize=12)
        st.pyplot(fig_g)

    # Fila 2: Densidad y Frecuencia de Género
    col_density, col_freq_gender = st.columns(2)

    with col_density:
        st.subheader("Densidad de Curva de Horas de Juego")
        fig_den, ax_den = plt.subplots(figsize=(10, 6))
        sns.kdeplot(df['PlayTimeHours'], fill=True, ax=ax_den, color=sns.color_palette(COLOR_PALETTE, as_cmap=True)(0.8))
        ax_den.set_xlabel("Horas de Juego (PlayTimeHours)", fontsize=12)
        ax_den.set_ylabel("Densidad", fontsize=12)
        st.pyplot(fig_den)

    with col_freq_gender:
        st.subheader("Frecuencias por Género")
        fig_fg, ax_fg = plt.subplots(figsize=(10, 6))
        sns.countplot(
            data=df, 
            x='Gender', 
            order=df['Gender'].value_counts().index, 
            palette=COLOR_PALETTE,
            ax=ax_fg
        )
        ax_fg.set_xlabel("Género", fontsize=12)
        ax_fg.set_ylabel("Frecuencia", fontsize=12)
        st.pyplot(fig_fg)

# --- 4. Análisis Filtrado ---
elif analysis_mode == "Análisis Filtrado":
    st.title("🔍 Análisis Segmentado con Filtros")
    
    # Mostrar filtros activos
    filter_text = []
    if gender_filter != 'Todos':
        filter_text.append(f"Género: {gender_filter}")
    filter_text.append(f"Edad: {age_filter[0]}-{age_filter[1]} años")
    
    st.markdown(f"**Filtros activos:** {' | '.join(filter_text)}")
    st.markdown(f"**Total de jugadores filtrados:** {len(filtered_df):,}")
    
    if filtered_df.empty:
        st.warning("⚠️ No hay datos disponibles para los filtros seleccionados.")
        st.stop()
    
    st.markdown("---")
    
    # --- KPIs Destacables del Segmento Filtrado ---
    st.header("📊 KPIs del Segmento Filtrado")
    
    col1, col2, col3, col4 = st.columns(4)
    
    # Calcular métricas del segmento
    total_filtered = len(filtered_df)
    avg_play_filtered = filtered_df['PlayTimeHours'].mean()
    conversion_filtered = (filtered_df['InGamePurchases'] > 0).sum() / total_filtered * 100
    avg_purchases_filtered = filtered_df['InGamePurchases'].mean()
    avg_level_filtered = filtered_df['PlayerLevel'].mean()
    
    # Calcular diferencias con la media general
    delta_play = ((avg_play_filtered - df['PlayTimeHours'].mean()) / df['PlayTimeHours'].mean()) * 100
    delta_conversion = conversion_filtered - ((df['InGamePurchases'] > 0).sum() / len(df) * 100)
    delta_purchases = ((avg_purchases_filtered - df['InGamePurchases'].mean()) / df['InGamePurchases'].mean()) * 100
    
    col1.metric(
        "Jugadores en Segmento", 
        f"{total_filtered:,}",
        delta=f"{(total_filtered/len(df)*100):.1f}% del total"
    )
    col2.metric(
        "Promedio Horas de Juego", 
        f"{avg_play_filtered:.2f} hrs",
        delta=f"{delta_play:+.1f}% vs general"
    )
    col3.metric(
        "Tasa de Conversión", 
        f"{conversion_filtered:.2f}%",
        delta=f"{delta_conversion:+.2f}% vs general"
    )
    col4.metric(
        "Compras In-Game Promedio", 
        f"{avg_purchases_filtered:.2f}",
        delta=f"{delta_purchases:+.1f}% vs general"
    )
    
    st.markdown("---")
    
    # --- Insight Destacable ---
    st.header("💡Lo Más Destacable")
    
    # Encontrar el género de juego más popular
    most_popular_genre = filtered_df['GameGenre'].value_counts().index[0]
    most_popular_genre_count = filtered_df['GameGenre'].value_counts().values[0]
    most_popular_genre_pct = (most_popular_genre_count / total_filtered) * 100
    
    # Encontrar el género de juego con mayor gasto
    top_spending_genre = filtered_df.groupby('GameGenre')['InGamePurchases'].mean().sort_values(ascending=False)
    highest_spending_genre = top_spending_genre.index[0]
    highest_spending_value = top_spending_genre.values[0]
    
    col_insight1, col_insight2 = st.columns(2)
    
    with col_insight1:
        st.info(f"""
        **🎯 Género Más Popular:** {most_popular_genre}
        - {most_popular_genre_pct:.1f}% de los jugadores en este segmento prefieren {most_popular_genre}
        - Total de jugadores: {most_popular_genre_count}
        """)
    
    with col_insight2:
        st.success(f"""
        **💰 Mayor Monetización:** {highest_spending_genre}
        - Promedio de compras: ${highest_spending_value:.2f}
        - Este género genera más ingresos en el segmento filtrado
        """)
    
    st.markdown("---")
    
    # --- Visualizaciones del Segmento ---
    st.header("📈 Análisis Visual del Segmento")
    
    # Gráfico 1: Distribución de Edades en el segmento
    st.subheader("1. Distribución de Edades en el Segmento")
    fig_age_seg, ax_age_seg = plt.subplots(figsize=(14, 6))
    sns.histplot(
        filtered_df['Age'], 
        kde=True, 
        bins=20, 
        ax=ax_age_seg, 
        color=sns.color_palette(COLOR_PALETTE)[1]
    )
    ax_age_seg.set_title(f'Distribución de Edades (Filtrado)', fontsize=14, fontweight='bold')
    ax_age_seg.set_xlabel('Edad', fontsize=12)
    ax_age_seg.set_ylabel('Frecuencia', fontsize=12)
    st.pyplot(fig_age_seg)
    
    st.markdown("---")
    
    # Gráfico 2: Género de Videojuego y Localización
    col_genre_viz, col_loc_viz = st.columns(2)
    
    with col_genre_viz:
        st.subheader("2. Género de Videojuego Preferido")
        fig_genre_seg, ax_genre_seg = plt.subplots(figsize=(10, 7))
        sns.countplot(
            data=filtered_df,
            y='GameGenre',
            order=filtered_df['GameGenre'].value_counts().index,
            palette=COLOR_PALETTE,
            ax=ax_genre_seg
        )
        ax_genre_seg.set_title('Preferencias de Género de Juego', fontsize=13, fontweight='bold')
        ax_genre_seg.set_xlabel('Frecuencia', fontsize=11)
        ax_genre_seg.set_ylabel('Género de Juego', fontsize=11)
        st.pyplot(fig_genre_seg)
    
    with col_loc_viz:
        st.subheader("3. Distribución por Localización")
        fig_loc_seg, ax_loc_seg = plt.subplots(figsize=(10, 7))
        sns.countplot(
            data=filtered_df,
            y='Location',
            order=filtered_df['Location'].value_counts().index,
            palette=COLOR_PALETTE,
            ax=ax_loc_seg
        )
        ax_loc_seg.set_title('Jugadores por Localización', fontsize=13, fontweight='bold')
        ax_loc_seg.set_xlabel('Frecuencia', fontsize=11)
        ax_loc_seg.set_ylabel('Localización', fontsize=11)
        st.pyplot(fig_loc_seg)
    
    st.markdown("---")
    
    # Gráfico 3: Dificultad por Género de Juego
    st.subheader("4. Dificultad Elegida por Género de Juego")
    fig_diff_seg, ax_diff_seg = plt.subplots(figsize=(14, 7))
    sns.countplot(
        data=filtered_df,
        y='GameGenre',
        hue='GameDifficulty',
        order=filtered_df['GameGenre'].value_counts().index,
        palette=COLOR_PALETTE,
        ax=ax_diff_seg
    )
    ax_diff_seg.set_title('Preferencias de Dificultad por Género de Juego', fontsize=14, fontweight='bold')
    ax_diff_seg.set_xlabel('Frecuencia', fontsize=12)
    ax_diff_seg.set_ylabel('Género de Juego', fontsize=12)
    ax_diff_seg.legend(title='Dificultad', fontsize=10)
    st.pyplot(fig_diff_seg)
    
    st.markdown("---")
    
    # Gráfico 4: Compras In-Game por Género de Juego
    st.subheader("5. Monetización: Compras In-Game por Género")
    purchases_summary = filtered_df.groupby('GameGenre')['InGamePurchases'].mean().sort_values(ascending=False).reset_index()
    
    fig_purchases_seg, ax_purchases_seg = plt.subplots(figsize=(14, 7))
    sns.barplot(
        data=purchases_summary,
        y='GameGenre',
        x='InGamePurchases',
        palette=COLOR_PALETTE,
        ax=ax_purchases_seg
    )
    ax_purchases_seg.set_title('Promedio de Compras In-Game por Género', fontsize=14, fontweight='bold')
    ax_purchases_seg.set_xlabel('Promedio de Compras ($)', fontsize=12)
    ax_purchases_seg.set_ylabel('Género de Juego', fontsize=12)
    st.pyplot(fig_purchases_seg)
    
    st.markdown("---")
    
st.caption("Hecho con Streamlit • Seaborn • Matplotlib • Pandas")

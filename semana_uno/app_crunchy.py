import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import streamlit as st
from ipywidgets import interact, widgets, VBox, HBox, Output
from IPython.display import display, clear_output
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="Crunchy Dashboard", layout="wide")
# Cargar datos
def load_data():
    return pd.read_csv("anime.csv")
 
df = load_data()

# Limpieza de datos
df["rating"] = df["rating"].fillna(0)
df["genre"] = df["genre"].fillna("unknown")
df["type"] = df["type"].fillna("unknown")
df['genre_list'] = df['genre'].str.split(', ')

# Separar géneros
genres_expanded = df.explode('genre_list')

print("=" * 80)
print("DASHBOARD DE KPIs - ANIME DATASET")
print("=" * 80)


# KPI 1: Rating Promedio General

def kpi_rating_promedio():
    rating_promedio = df[df['rating'] > 0]['rating'].mean()
    rating_mediano = df[df['rating'] > 0]['rating'].median()
    total_animes = len(df)
    animes_con_rating = len(df[df['rating'] > 0])
    
    print("\n📊 KPI 1: ANÁLISIS DE RATING")
    print("-" * 80)
    print(f"Rating Promedio General: {rating_promedio:.2f} / 10")
    print(f"Rating Mediano: {rating_mediano:.2f} / 10")
    print(f"Total de Animes: {total_animes:,}")
    print(f"Animes con Rating: {animes_con_rating:,}")
    print(f"% Animes con Rating: {(animes_con_rating/total_animes)*100:.1f}%")
    
    # Visualización
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    
    # Distribución de ratings
    df[df['rating'] > 0]['rating'].hist(bins=30, edgecolor='black', ax=axes[0], color='skyblue')
    axes[0].axvline(rating_promedio, color='red', linestyle='--', linewidth=2, label=f'Promedio: {rating_promedio:.2f}')
    axes[0].set_xlabel('Rating')
    axes[0].set_ylabel('Frecuencia')
    axes[0].set_title('Distribución de Ratings')
    axes[0].legend()
    axes[0].grid(axis='y', alpha=0.3)
    
    # Box plot
    df[df['rating'] > 0].boxplot(column='rating', ax=axes[1])
    axes[1].set_ylabel('Rating')
    axes[1].set_title('Box Plot de Ratings')
    axes[1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.show()

# KPI 2: Top Géneros por Popularidad

def kpi_generos_populares(top_n=10):
    genre_stats = genres_expanded.groupby('genre_list').agg({
        'rating': 'mean',
        'members': 'sum',
        'anime_id': 'count'
    }).rename(columns={'anime_id': 'count'}).sort_values('members', ascending=False)
    
    top_genres = genre_stats.head(top_n)
    
    print(f"\n🎭 KPI 2: TOP {top_n} GÉNEROS MÁS POPULARES")
    print("-" * 80)
    print(f"{'Género':<25} {'Total Miembros':>15} {'Rating Prom':>12} {'# Animes':>10}")
    print("-" * 80)
    for idx, (genre, row) in enumerate(top_genres.iterrows(), 1):
        print(f"{idx}. {genre:<22} {int(row['members']):>15,} {row['rating']:>11.2f} {int(row['count']):>10}")
    
    # Visualización
    fig, axes = plt.subplots(1, 2, figsize=(15, 6))
    
    # Gráfico de barras - Miembros
    top_genres['members'].plot(kind='barh', ax=axes[0], color='coral')
    axes[0].set_xlabel('Total de Miembros')
    axes[0].set_title(f'Top {top_n} Géneros por Popularidad')
    axes[0].grid(axis='x', alpha=0.3)
    
    # Gráfico de barras - Rating
    top_genres['rating'].plot(kind='barh', ax=axes[1], color='lightgreen')
    axes[1].set_xlabel('Rating Promedio')
    axes[1].set_title(f'Top {top_n} Géneros por Rating')
    axes[1].grid(axis='x', alpha=0.3)
    
    plt.tight_layout()
    plt.show()

# KPI 3: Análisis por Tipo de Programa
def kpi_tipo_programa():
    type_stats = df[df['rating'] > 0].groupby('type').agg({
        'rating': 'mean',
        'members': 'sum',
        'anime_id': 'count'
    }).rename(columns={'anime_id': 'count'}).sort_values('count', ascending=False)
    
    print("\n📺 KPI 3: ANÁLISIS POR TIPO DE PROGRAMA")
    print("-" * 80)
    print(f"{'Tipo':<15} {'Cantidad':>10} {'Rating Prom':>12} {'Total Miembros':>15}")
    print("-" * 80)
    for tipo, row in type_stats.iterrows():
        print(f"{tipo:<15} {int(row['count']):>10,} {row['rating']:>11.2f} {int(row['members']):>15,}")
    
    # Visualización
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # Cantidad por tipo
    type_stats['count'].plot(kind='bar', ax=axes[0], color='steelblue')
    axes[0].set_xlabel('Tipo de Programa')
    axes[0].set_ylabel('Cantidad')
    axes[0].set_title('Cantidad de Animes por Tipo')
    axes[0].tick_params(axis='x', rotation=45)
    axes[0].grid(axis='y', alpha=0.3)
    
    # Rating por tipo
    type_stats['rating'].plot(kind='bar', ax=axes[1], color='orange')
    axes[1].set_xlabel('Tipo de Programa')
    axes[1].set_ylabel('Rating Promedio')
    axes[1].set_title('Rating Promedio por Tipo')
    axes[1].tick_params(axis='x', rotation=45)
    axes[1].grid(axis='y', alpha=0.3)
    
    plt.tight_layout()
    plt.show()


# KPI 4: Top Animes
def kpi_top_animes(criterio='rating', top_n=10):
    if criterio == 'rating':
        top_animes = df.nlargest(top_n, 'rating')[['name', 'rating', 'members', 'type']]
        titulo = "RATING"
    else:
        top_animes = df.nlargest(top_n, 'members')[['name', 'rating', 'members', 'type']]
        titulo = "POPULARIDAD (Miembros)"
    
    print(f"\n🏆 KPI 4: TOP {top_n} ANIMES POR {titulo}")
    print("-" * 80)
    print(f"{'#':<3} {'Nombre':<40} {'Rating':>8} {'Miembros':>12} {'Tipo':<10}")
    print("-" * 80)
    for idx, (_, anime) in enumerate(top_animes.iterrows(), 1):
        nombre_corto = anime['name'][:37] + '...' if len(anime['name']) > 40 else anime['name']
        print(f"{idx:<3} {nombre_corto:<40} {anime['rating']:>8.2f} {int(anime['members']):>12,} {anime['type']:<10}")


def crear_dashboard():
    output = Output()
    
    # Botones para KPIs
    btn_kpi1 = widgets.Button(description='📊 Rating General', 
                               button_style='info',
                               layout=widgets.Layout(width='200px', height='40px'))
    btn_kpi2 = widgets.Button(description='🎭 Géneros Populares', 
                               button_style='success',
                               layout=widgets.Layout(width='200px', height='40px'))
    btn_kpi3 = widgets.Button(description='📺 Tipos de Programa', 
                               button_style='warning',
                               layout=widgets.Layout(width='200px', height='40px'))
    btn_kpi4_rating = widgets.Button(description='🏆 Top por Rating', 
                                      button_style='danger',
                                      layout=widgets.Layout(width='200px', height='40px'))
    btn_kpi4_pop = widgets.Button(description='⭐ Top por Popularidad', 
                                   button_style='danger',
                                   layout=widgets.Layout(width='200px', height='40px'))
    
    # Slider para top N
    slider_top = widgets.IntSlider(value=10, min=5, max=20, step=5,
                                   description='Top N:',
                                   style={'description_width': 'initial'})
    
    def on_kpi1_click(b):
        with output:
            clear_output(wait=True)
            kpi_rating_promedio()
    
    def on_kpi2_click(b):
        with output:
            clear_output(wait=True)
            kpi_generos_populares(slider_top.value)
    
    def on_kpi3_click(b):
        with output:
            clear_output(wait=True)
            kpi_tipo_programa()
    
    def on_kpi4_rating_click(b):
        with output:
            clear_output(wait=True)
            kpi_top_animes('rating', slider_top.value)
    
    def on_kpi4_pop_click(b):
        with output:
            clear_output(wait=True)
            kpi_top_animes('members', slider_top.value)
    
    btn_kpi1.on_click(on_kpi1_click)
    btn_kpi2.on_click(on_kpi2_click)
    btn_kpi3.on_click(on_kpi3_click)
    btn_kpi4_rating.on_click(on_kpi4_rating_click)
    btn_kpi4_pop.on_click(on_kpi4_pop_click)
    
    # Layout
    buttons_row1 = HBox([btn_kpi1, btn_kpi2, btn_kpi3])
    buttons_row2 = HBox([btn_kpi4_rating, btn_kpi4_pop, slider_top])
    
    dashboard = VBox([
        widgets.HTML('<h2 style="text-align: center; color: #2E86AB;">🎌 Dashboard de KPIs - Anime Dataset</h2>'),
        widgets.HTML('<p style="text-align: center;">Selecciona un KPI para visualizar:</p>'),
        buttons_row1,
        buttons_row2,
        output
    ])
    
    display(dashboard)
    
    # Mostrar resumen inicial
    with output:
        print("\n✨ Bienvenido al Dashboard de KPIs de Anime")
        print("\n📌 Resumen del Dataset:")
        print(f"   • Total de animes: {len(df):,}")
        print(f"   • Rating promedio: {df[df['rating'] > 0]['rating'].mean():.2f}")
        print(f"   • Tipos de programas: {df['type'].nunique()}")
        print(f"   • Total de miembros: {df['members'].sum():,}")
        print("\n👆 Haz clic en los botones de arriba para ver los KPIs detallados")

# Ejecutar dashboard
crear_dashboard()


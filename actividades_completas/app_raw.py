import streamlit as st
import pandas as pd
import boto3
import json
from io import StringIO
import time # Para el temporizador de actualización
from datetime import datetime # Para convertir a datetime si es necesario


# --- Configuración S3 ---
BUCKET_NAME = "xideralaws-curso-benjamin2"
PREFIX = "raw/"
# Inicializar el cliente S3 una sola vez
# st.cache_resource asegura que el cliente boto3 se inicialice una vez.
@st.cache_resource
def get_s3_client():
    return boto3.client("s3")

s3 = get_s3_client()

# --- Funciones de Carga y Procesamiento de Datos ---

@st.cache_data(ttl=60) # Se refrescará automáticamente cada 60 segundos
def actualizar_datos_desde_s3(timestamp):
    """
    Carga todos los archivos JSON del prefijo S3, los concatena y los procesa.
    El argumento `timestamp` se usa para forzar la actualización del caché.
    """
    try:
        # 1. Listar objetos
        response = s3.list_objects_v2(Bucket=BUCKET_NAME, Prefix=PREFIX)
        
        # Si no hay contenido, retorna un DataFrame vacío
        if 'Contents' not in response:
            st.warning("No se encontraron archivos en la ruta especificada.")
            return pd.DataFrame()
        
        data_frames = []
        
        # 2. Descargar y procesar cada JSON
        for obj in response["Contents"]:
            key = obj["Key"]
            if key.endswith(".json"):
                file_obj = s3.get_object(Bucket=BUCKET_NAME, Key=key)
                content = file_obj["Body"].read().decode("utf-8")
                json_data = json.loads(content)
                # Normalizar el JSON a DataFrame
                df_temp = pd.json_normalize(json_data)
                data_frames.append(df_temp)

        # 3. Concatenar DataFrames
        if data_frames:
            df = pd.concat(data_frames, ignore_index=True)
            
            # 4. Procesamiento: convertir 'timestamp' a datetime
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            return df
        else:
            return pd.DataFrame()
            
    except Exception as e:
        st.error(f"Error al cargar o procesar los datos de S3: {e}")
        return pd.DataFrame()

def generar_metricas_estado(df_base: pd.DataFrame):
    """
    Filtra el DataFrame base y calcula el conteo de estados por servidor.
    """
    if df_base.empty:
        return pd.DataFrame({'status':[]}) # Retorna un df con la columna 'status' esperada

    
    # Agrupar por 'server_id' y luego contar los valores de 'status'
    result_series = df_base.groupby('server_id')['status'].value_counts()
    
    # Convertir el resultado a DataFrame para una mejor visualización en Streamlit
    result_df = result_series.unstack(fill_value=0)
    
    # Asegurarse de que las columnas 'OK', 'WARN', 'ERROR' existan, aunque estén en 0
    # Esto es opcional, pero ayuda a la consistencia del dashboard
    status_columns = ['OK', 'WARN', 'ERROR']
    for col in status_columns:
        if col not in result_df.columns:
            result_df[col] = 0
            
    result_df = result_df[status_columns]
    result_df.index.name = 'server_id'
    
    return result_df

# --- Layout del Dashboard Streamlit ---

st.set_page_config(
    page_title="Dashboard de Métricas de Servidores",
    layout="wide",
)

st.title("Monitoreo en Tiempo Real de Servidores 📊")

# Sección para el botón de actualización y el temporizador
col1, col2 = st.columns([1, 4])

# Botón de actualización: forzar un nuevo timestamp para romper el caché
if col1.button('Actualizar Datos'):
    st.session_state['last_update'] = datetime.now()
    st.toast('¡Datos actualizados!', icon='✅')

# Usar st.empty() para un placeholder de texto que se actualizará con st.info
info_placeholder = col2.empty()

# Inicializar 'last_update' en el Session State si no existe
if 'last_update' not in st.session_state:
    st.session_state['last_update'] = datetime.now()

# Forzar la recarga de datos pasando el timestamp del botón como argumento
df_actualizado = actualizar_datos_desde_s3(st.session_state['last_update'])

# Mostrar la hora de la última actualización
info_placeholder.info(f"Última actualización de datos: {st.session_state['last_update'].strftime('%Y-%m-%d %H:%M:%S')}")


# --- Visualización de Métricas ---

if not df_actualizado.empty:
    
    # Generar el DataFrame de métricas de estado
    metricas_df = generar_metricas_estado(df_actualizado)
    
    st.header("Conteo de Estados por Servidor")
    
    # Usar columnas de Streamlit para un layout de tipo "card"
    # Mostrar las métricas totales
    total_ok = metricas_df['OK'].sum()
    total_warn = metricas_df['WARN'].sum()
    total_error = metricas_df['ERROR'].sum()

    col_ok, col_warn, col_error = st.columns(3)
    
    col_ok.metric("Total OK", total_ok)
    col_warn.metric("Total WARN", total_warn)
    col_error.metric("Total ERROR", total_error)
    
    st.divider()

    # Mostrar la tabla de conteo de estados por servidor
    st.subheader("Detalle por `server_id`")
    st.dataframe(metricas_df)
    
    # Opcional: Mostrar un gráfico de barras
    st.subheader("Gráfico de Conteo de Estados")
    st.bar_chart(metricas_df)
    
    st.divider()
    
    # Opcional: Mostrar los datos crudos
    st.subheader("Vista Previa de Datos Crudos")
    st.dataframe(df_actualizado.tail(10)) 

else:
    st.warning("El DataFrame de métricas está vacío. Verifica la conexión a S3 y el contenido del bucket.")

time.sleep(10) # Esperar 10 segundos
st.rerun() # Forzar la re-ejecución


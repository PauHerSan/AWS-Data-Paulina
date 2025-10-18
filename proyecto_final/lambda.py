import json
import urllib.parse
import boto3
import pandas as pd
import io
import os

# Inicializar el cliente de S3
s3 = boto3.client('s3')


PROCESSED_FOLDER = 'processed/'

def lambda_handler(event, context):
    
    
    # 1. Obtener la información del archivo que disparó el evento
    try:
        bucket = event['Records'][0]['s3']['bucket']['name']
        key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
        print(f"Evento disparado por el archivo: s3://{bucket}/{key}")
    except KeyError:
        print("Error: El evento no parece provenir de S3 o le faltan campos.")
        return {'statusCode': 400, 'body': json.dumps('Error de evento S3.')}
    except Exception as e:
        print(f"Error general al obtener info del evento: {e}")
        raise e

    # 2. Leer el archivo CSV de S3
    try:
        # Obtener el objeto S3
        obj = s3.get_object(Bucket=bucket, Key=key)
        # Leer el contenido del archivo en memoria
        data = obj['Body'].read()
        # Cargar los datos en un DataFrame de Pandas
        df = pd.read_csv(io.BytesIO(data))
        print(f"CSV cargado con éxito. Filas iniciales: {len(df)}")
    except Exception as e:
        print(f"Error al leer o cargar el CSV de S3: {e}")
       
        return {'statusCode': 500, 'body': json.dumps(f'Error al procesar el archivo: {e}')}

    
    # 3. Realizar la Transformación de Datos (Parte académica del proyecto)
    
    # --- Creación de la Métrica Clave ---
    # Calculamos el tiempo total de juego por semana en minutos
    df['WeeklyPlayTimeMinutes'] = df['SessionsPerWeek'] * df['AvgSessionDurationMinutes']
    
    # --- Creación de la Columna de Segmentación por Edad ---
    # Categorizar la edad en rangos
    bins = [18, 25, 35, 99] # Asumiendo 18 es el mínimo
    labels = ['Joven (<25)', 'Adulto Joven (25-35)', 'Adulto (>35)']
    df['AgeSegment'] = pd.cut(df['Age'], bins=bins, labels=labels, right=False)
    
    # Seleccionar y reordenar las columnas que deseas guardar (limpieza)
    columns_to_keep = [
        'PlayerID', 'AgeSegment', 'Gender', 'Location', 'GameGenre',
        'PlayTimeHours', 'WeeklyPlayTimeMinutes', 'InGamePurchases', 
        'GameDifficulty', 'PlayerLevel', 'AchievementsUnlocked', 'EngagementLevel'
    ]
    df_processed = df[columns_to_keep]

    print(f"Transformación completada. Se agregó 'WeeklyPlayTimeMinutes' y 'AgeSegment'.")


    # 4. Guardar el DataFrame Procesado de vuelta a S3
    
    # Crear un buffer en memoria para el nuevo CSV
    csv_buffer = io.StringIO()
    df_processed.to_csv(csv_buffer, index=False)
    
    # Definir la nueva clave (ruta) del archivo en S3 (ejemplo: processed/online_gaming_insights_processed.csv)
    original_filename = os.path.basename(key)
    new_key = PROCESSED_FOLDER + original_filename.replace('.csv', '_processed.csv')
    
    # Subir el archivo procesado
    s3.put_object(
        Bucket=bucket,
        Key=new_key,
        Body=csv_buffer.getvalue()
    )
    
    print(f"Archivo procesado guardado con éxito en s3://{bucket}/{new_key}")

    # Retornar una respuesta exitosa
    return {
        'statusCode': 200,
        'body': json.dumps(f'Procesamiento completado. Archivo guardado en {new_key}')
    }
"""
Script de inicialización automática para ClickHouse
"""

import time
import os
from clickhouse_driver import Client

def wait_for_clickhouse(max_retries=30):
    """
    Esperar a que ClickHouse esté listo.
    """

    print("Esperando a que ClickHouse esté listo...")
    
    for i in range(max_retries):
        try:
            client = Client(
                host='clickhouse',
                port=9000,
                user='admin',
                password='admin123'
            )
            client.execute('SELECT 1')
            print("ClickHouse está listo!")
            return client
        except Exception as e:
            print(f"   Intento {i+1}/{max_retries}: {e}")
            time.sleep(5)
    
    raise Exception("ClickHouse no respondió después de todos los intentos")

def create_database_and_tables(client):
    """
    Crear base de datos y tablas.
    """
    
    queries = [
        "CREATE DATABASE IF NOT EXISTS sensors_db",
        
        """CREATE TABLE IF NOT EXISTS sensors_db.sensor_data (
            sensor_id String,
            ubicacion String,
            lat Float64,
            lon Float64,
            temperatura Float32,
            humedad UInt8,
            calidad_aire UInt8,
            ruido_db UInt8,
            trafico_nivel UInt8,
            timestamp DateTime,
            timestamp_ms UInt64,
            date Date MATERIALIZED toDate(timestamp)
        ) ENGINE = MergeTree()
        PARTITION BY date
        ORDER BY (timestamp, sensor_id)
        TTL timestamp + INTERVAL 30 DAY""",
        
        """CREATE TABLE IF NOT EXISTS sensors_db.sensor_hourly (
            hour DateTime,
            ubicacion String,
            temp_promedio Float32,
            temp_maxima Float32,
            temp_minima Float32,
            humedad_promedio Float32,
            aqi_promedio Float32,
            ruido_promedio Float32,
            num_lecturas UInt32
        ) ENGINE = MergeTree()
        ORDER BY (hour, ubicacion)""",
        
        """CREATE MATERIALIZED VIEW IF NOT EXISTS sensors_db.sensor_hourly_mv
        TO sensors_db.sensor_hourly
        AS SELECT
            toStartOfHour(timestamp) AS hour,
            ubicacion,
            round(avg(temperatura), 1) AS temp_promedio,
            max(temperatura) AS temp_maxima,
            min(temperatura) AS temp_minima,
            round(avg(humedad), 1) AS humedad_promedio,
            round(avg(calidad_aire), 1) AS aqi_promedio,
            round(avg(ruido_db), 1) AS ruido_promedio,
            count() AS num_lecturas
        FROM sensors_db.sensor_data
        GROUP BY hour, ubicacion"""
    ]
    
    print("Creando base de datos y tablas...")
    
    for i, query in enumerate(queries, 1):
        try:
            client.execute(query)
            print(f"Query {i}/{len(queries)} ejecutada correctamente")
        except Exception as e:
            print(f"Error en query {i}: {e}")
            raise
    
    tables = client.execute("SHOW TABLES FROM sensors_db")
    print(f"Tablas creadas: {[table[0] for table in tables]}")

def main():
    """
    Función principal.
    """

    print("Inicializador automático de ClickHouse")
    print("-" * 40)
    
    try:

        client = wait_for_clickhouse()
        
        create_database_and_tables(client)
        
        print("ClickHouse inicializado correctamente!")
        
    except Exception as e:
        print(f"Error fatal: {e}")
        exit(1)

if __name__ == "__main__":
    main()
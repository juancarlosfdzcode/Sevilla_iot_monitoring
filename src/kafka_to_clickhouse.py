#!/usr/bin/env python3
"""
Consumer que lee datos de Kafka e inserta en ClickHouse
"""

import json
import time
import os
from datetime import datetime
from typing import Dict, Any, List
from kafka import KafkaConsumer
from clickhouse_driver import Client

class KafkaClickHouseConsumer:
    def __init__(self):
        # Configuración Kafka
        self.kafka_broker = os.getenv('KAFKA_BROKER', 'localhost:9092')
        self.topic = os.getenv('TOPIC_NAME', 'sevilla-sensors')
        
        # Configuración ClickHouse
        self.ch_host = os.getenv('CLICKHOUSE_HOST', 'localhost')
        self.ch_port = int(os.getenv('CLICKHOUSE_PORT', '9000'))
        self.ch_user = os.getenv('CLICKHOUSE_USER', 'admin')
        self.ch_password = os.getenv('CLICKHOUSE_PASSWORD', 'admin123')
        
        self.consumer = None
        self.clickhouse_client = None
        
    def connect_kafka(self) -> bool:
        """Conectar a Kafka consumer"""
        try:
            self.consumer = KafkaConsumer(
                self.topic,
                bootstrap_servers=[self.kafka_broker],
                value_deserializer=lambda m: json.loads(m.decode('utf-8')),
                key_deserializer=lambda m: m.decode('utf-8') if m else None,
                group_id='clickhouse-consumer-group',
                auto_offset_reset='latest',
                api_version=(2, 0, 2),
                request_timeout_ms=60000,
                connections_max_idle_ms=300000
            )
            print(f"✅ Conectado a Kafka: {self.kafka_broker}")
            return True
        except Exception as e:
            print(f"❌ Error conectando a Kafka: {e}")
            return False
    
    def connect_clickhouse(self) -> bool:
        """Conectar a ClickHouse"""
        try:
            self.clickhouse_client = Client(
                host=self.ch_host,
                port=self.ch_port,
                user=self.ch_user,
                password=self.ch_password,
                database='sensors_db'
            )
            # Test de conexión
            result = self.clickhouse_client.execute('SELECT 1')
            print(f"✅ Conectado a ClickHouse: {self.ch_host}:{self.ch_port}")
            return True
        except Exception as e:
            print(f"❌ Error conectando a ClickHouse: {e}")
            return False
    
    def parse_sensor_data(self, kafka_message: Dict[str, Any]) -> tuple:
        """Parsear mensaje de Kafka para ClickHouse"""
        try:
            # Extraer datos
            sensor_id = kafka_message.get('sensor_id')
            ubicacion = kafka_message.get('ubicacion')
            coordenadas = kafka_message.get('coordenadas', {})
            datos = kafka_message.get('datos', {})
            
            # Parsear timestamp
            timestamp_str = kafka_message.get('timestamp')
            timestamp = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
            
            # Crear tupla para ClickHouse
            return (
                sensor_id,
                ubicacion,
                coordenadas.get('lat', 0.0),
                coordenadas.get('lon', 0.0),
                datos.get('temperatura', 0.0),
                datos.get('humedad', 0),
                datos.get('calidad_aire', 0),
                datos.get('ruido_db', 0),
                datos.get('trafico_nivel', 0),
                timestamp,
                kafka_message.get('timestamp_unix', int(timestamp.timestamp() * 1000))
            )
        except Exception as e:
            print(f"❌ Error parseando mensaje: {e}")
            return None
    
    def insert_batch(self, batch: List[tuple]) -> bool:
        """Insertar batch en ClickHouse"""
        try:
            query = """
            INSERT INTO sensor_data 
            (sensor_id, ubicacion, lat, lon, temperatura, humedad, 
             calidad_aire, ruido_db, trafico_nivel, timestamp, timestamp_ms)
            VALUES
            """
            
            self.clickhouse_client.execute(query, batch)
            return True
        except Exception as e:
            print(f"❌ Error insertando en ClickHouse: {e}")
            return False
    
    def run(self):
        """Ejecutar consumer principal"""
        print("🌆 Kafka → ClickHouse Consumer para Sevilla IoT")
        print("-" * 50)
        
        # Conectar servicios
        if not self.connect_kafka():
            return
        if not self.connect_clickhouse():
            return
        
        print("📡 Escuchando mensajes de Kafka...")
        print("📊 Insertando datos en ClickHouse en tiempo real...")
        print("⏹️ Presiona Ctrl+C para parar\n")
        
        batch = []
        batch_size = 10  # Insertar cada 10 mensajes
        messages_processed = 0
        
        try:
            for message in self.consumer:
                # Parsear mensaje
                parsed_data = self.parse_sensor_data(message.value)
                if parsed_data:
                    batch.append(parsed_data)
                    messages_processed += 1
                    
                    # Mostrar progreso
                    sensor_id = message.value.get('sensor_id', 'UNKNOWN')
                    temp = message.value.get('datos', {}).get('temperatura', 0)
                    timestamp = datetime.now().strftime("%H:%M:%S")
                    
                    print(f"📥 {timestamp} | {sensor_id} | 🌡️{temp}°C | Batch: {len(batch)}/{batch_size}")
                    
                    # Insertar batch cuando esté lleno
                    if len(batch) >= batch_size:
                        if self.insert_batch(batch):
                            print(f"✅ Insertados {len(batch)} registros en ClickHouse")
                        batch = []
                        
        except KeyboardInterrupt:
            print("\n⏹️ Deteniendo consumer...")
            
            # Insertar batch restante
            if batch:
                if self.insert_batch(batch):
                    print(f"✅ Insertados {len(batch)} registros finales")
        
        print(f"\n📊 Consumer finalizado. Total mensajes procesados: {messages_processed}")

if __name__ == "__main__":
    consumer = KafkaClickHouseConsumer()
    consumer.run()
"""
Sensor IoT que envía datos a Kafka en tiempo real
"""

import json
import time
import random
import os
from datetime import datetime
from typing import Dict, List, Any, Optional

try:
    from kafka import KafkaProducer
    KAFKA_AVAILABLE = True
except ImportError:
    KAFKA_AVAILABLE = False
    print("kafka-python no instalado. Modo simulación activado.")

class SensorKafka:
    def __init__(self, sensor_id: str, ubicacion: str, lat: float, lon: float, kafka_enabled: bool = False):
        self.sensor_id: str = sensor_id
        self.ubicacion: str = ubicacion
        self.lat: float = lat
        self.lon: float = lon
        self.kafka_enabled: bool = kafka_enabled and KAFKA_AVAILABLE
        self.producer: Optional[KafkaProducer] = None
        
        if self.kafka_enabled:
            self._conectar_kafka()
    
    def _conectar_kafka(self) -> None:
        """
        Conectar a Kafka.
        """

        try:
            kafka_broker = os.getenv('KAFKA_BROKER', 'localhost:9092')
            self.producer = KafkaProducer(
                bootstrap_servers=[kafka_broker],
                value_serializer=lambda v: json.dumps(v).encode('utf-8'),
                key_serializer=lambda k: k.encode('utf-8') if k else None
            )
            print(f"Sensor {self.sensor_id} conectado a Kafka: {kafka_broker}")
        except Exception as e:
            print(f"Error conectando a Kafka: {e}")
            self.kafka_enabled = False
    
    def generar_lectura(self) -> Dict[str, Any]:
        """
        Genera una lectura del sensor.
        """

        if "CENTRO" in self.sensor_id:
            temp_base: float = 25.0
            humedad_base: int = 60
        elif "TRIANA" in self.sensor_id:
            temp_base = 23.0
            humedad_base = 70
        elif "PARQUE" in self.sensor_id:
            temp_base = 21.0
            humedad_base = 75
        else:
            temp_base = 24.0
            humedad_base = 65
        
        now = datetime.now()
        
        return {
            "sensor_id": self.sensor_id,
            "ubicacion": self.ubicacion,
            "coordenadas": {"lat": self.lat, "lon": self.lon},
            "datos": {
                "temperatura": round(temp_base + random.uniform(-5, 10), 1),
                "humedad": max(30, min(90, humedad_base + random.randint(-15, 15))),
                "calidad_aire": random.randint(1, 4),
                "ruido_db": random.randint(40, 75),
                "trafico_nivel": random.randint(1, 5)
            },
            "timestamp": now.isoformat(),
            "timestamp_unix": int(now.timestamp())
        }
    
    def enviar_lectura(self, lectura: Dict[str, Any]) -> bool:
        """
        Envía lectura a Kafka o guarda en archivo.
        """

        if self.kafka_enabled and self.producer:
            try:
                topic = os.getenv('TOPIC_NAME', 'sevilla-sensors')
                future = self.producer.send(
                    topic, 
                    key=self.sensor_id, 
                    value=lectura
                )
                future.get(timeout=5)

                return True
            
            except Exception as e:
                print(f"Error enviando a Kafka: {e}")
                return False
        else:

            timestamp = lectura["timestamp"].replace(":", "-").split(".")[0]
            filename = f"data/sensor_{self.sensor_id}_{timestamp}.json"
            os.makedirs("data", exist_ok=True)
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(lectura, f, indent=2, ensure_ascii=False)

            return True

class RedSensoresKafka:
    def __init__(self):
        kafka_enabled = os.getenv('KAFKA_ENABLED', 'false').lower() == 'true'
        
        self.sensores: List[SensorKafka] = [
            SensorKafka("SEV-CENTRO-001", "Centro Histórico", 37.3886, -5.9823, kafka_enabled),
            SensorKafka("SEV-TRIANA-002", "Triana", 37.3838, -6.0021, kafka_enabled),
            SensorKafka("SEV-PARQUE-003", "Parque María Luisa", 37.3721, -5.9874, kafka_enabled),
            SensorKafka("SEV-NERVION-004", "Nervión", 37.3914, -5.9750, kafka_enabled)
        ]
        
        self.intervalo = int(os.getenv('SENSOR_INTERVAL', '10'))
        self.kafka_enabled = kafka_enabled
    
    def ejecutar_streaming(self, duracion_segundos: int = 120) -> None:
        """
        Ejecuta streaming continuo de sensores.
        """

        print("Red de Sensores IoT Sevilla - Modo Streaming")
        print(f"Kafka habilitado: {'SÍ' if self.kafka_enabled else 'NO (modo archivo)'}")
        print(f"{len(self.sensores)} sensores activos")
        print(f"Enviando datos cada {self.intervalo} segundos")
        print("-" * 40)
        
        inicio = time.time()
        contador = 0
        
        try:
            while time.time() - inicio < duracion_segundos:
                contador += 1
                timestamp = datetime.now().strftime("%H:%M:%S")
                
                print(f"Ciclo #{contador} - {timestamp}")
                print("-" * 40) 
                
                for sensor in self.sensores:
                    lectura = sensor.generar_lectura()
                    enviado = sensor.enviar_lectura(lectura)
                    datos = lectura["datos"]

                    print(f"{sensor.sensor_id}: "
                          f"{datos['temperatura']}°C | "
                          f"{datos['humedad']}% | "
                          f"{datos['ruido_db']}dB | "
                          f"AQI: {datos['calidad_aire']}"
                          f"{datos['trafico_nivel']}")
                    
                    if enviado:
                        print(f'Documentos generados')
                
                print()
                time.sleep(self.intervalo)
                
        except KeyboardInterrupt:
            print("\nStreaming detenido por el usuario")
        
        print(f"\n Streaming finalizado. {contador} ciclos completados.")
        
        for sensor in self.sensores:
            if sensor.producer:
                sensor.producer.flush()
                sensor.producer.close()

if __name__ == "__main__":
    red = RedSensoresKafka()
    red.ejecutar_streaming()
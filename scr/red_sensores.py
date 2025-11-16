"""
Red de sensores IoT en Sevilla.
"""

import json
import time
import random
import os
from datetime import datetime
from typing import Any, Dict, List

class SensorIoT:
    def __init__(self, sensor_id: str, ubicacion: str, lat: float, lon: float) -> None:
        self.sensor_id: str = sensor_id
        self.ubicacion: str = ubicacion
        self.lat: float = lat
        self.lon: float = lon
    
    def generar_lectura(self) -> Dict[str, Any]:
        """
        Generar una lectura con variaciones por zona.
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
    
        return {
            "sensor_id": self.sensor_id,
            "ubicacion": self.ubicacion,
            "coordenadas": {"lat": self.lat, "lon": self.lon},
            "datos": {
                "temperatura": round(temp_base + random.uniform(-5, 10), 1),
                "humedad": max(30, min(90, humedad_base + random.randint(-15, 15))),
                "calidad_aire": random.randint(1, 4),
                "ruido_db": random.randint(40, 75)
            },
            "timestamp": datetime.now().isoformat()
        }

class RedSensores:

    def __init__(self) -> None:
        self.sensores: List[SensorIoT] = [
            SensorIoT("SEV-CENTRO-001", "Centro Histórico", 37.3886, -5.9823),
            SensorIoT("SEV-TRIANA-002", "Triana", 37.3838, -6.0021), 
            SensorIoT("SEV-PARQUE-003", "Parque María Luisa", 37.3721, -5.9874),
            SensorIoT("SEV-NERVION-004", "Nervión", 37.3829, -5.9732)
        ]
        
        os.makedirs('data', exist_ok=True)
    
    def ejecutar_ciclo(self) -> List[Dict[str, Any]]:
        """
        Ejecuta un ciclo completo de todos los sensores.
        """

        timestamp: str = datetime.now().strftime("%Y%m%d_%H%M%S")
        archivo: str = f"data/lecturas_{timestamp}.json"
        
        lecturas: List[Dict[str, Any]] = []
        
        print(f"Ciclo {timestamp}")
        print('-' * 40)

        for sensor in self.sensores:
            lectura: Dict[str, Any] = sensor.generar_lectura()
            lecturas.append(lectura)
            
            datos: Dict[str, Any] = lectura["datos"]
            print(f"{lectura['sensor_id']}: "
                  f"{datos['temperatura']}°C | "
                  f"{datos['humedad']}% | "
                  f"{datos['ruido_db']}dB"
                  f"AQI: {datos['calidad_aire']}"
                  )
        
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(lecturas, f, indent=2, ensure_ascii=False)
        
        print(f"Guardado en {archivo}")
        
        return lecturas
    
    def ejecutar_red(self, ciclos: int = 5) -> None:
        """
        Ejecuta la red de sensores.
        """

        print("Red de Sensores IoT Sevilla")
        print(f"{len(self.sensores)} sensores activos")
        print("-" * 40)
        
        for i in range(ciclos):
            lecturas: List[Dict[str, Any]] = self.ejecutar_ciclo()
            
            print(f"Ciclo {i+1}/{ciclos} completado\n")
            time.sleep(10)
        
        print(f"Red finalizada. Archivos en directorio 'data/'")

if __name__ == "__main__":
    red: RedSensores = RedSensores()
    red.ejecutar_red()
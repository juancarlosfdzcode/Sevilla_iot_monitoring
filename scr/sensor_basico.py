"""
Sensor IoT básico para Centro Histórico de Sevilla.
"""

import json
import time
import random
from datetime import datetime
from typing import Dict

def generar_lectura() -> Dict:
    """
    Genera una lectura del sensor.
    """

    return {
        'sensor_id': 'SEV-CENTRO-001',
        'ubicacion': 'Centro Histórico',
        'coordenadas': {'lat': 37.3886, 'lon': -5.9823},
        'datos': {
            'temperatura': round(random.uniform(15.0,35.0),1),
            'humedad': random.randint(40, 80),
            'calidad_aire': random.randint(1, 4)
        },
        'timestamp': datetime.now().isoformat()
    }

def ejecutar_sensor():
    """
    Ejecuta el sensor continuamente.
    """

    print('Sensor SEV-CENTRO-001 - Iniciando...')
    print('-' * 40)

    for i in range(10):
        lectura = generar_lectura()
        datos = lectura['datos']
        hora = lectura['timestamp']

        print(f"#{i+1:02d} | {datos['temperatura']}ºC | {datos['humedad']}% | AQI: {datos['calidad_aire']} | {hora}")

    print('-' * 40)
    print('Sensor finalizado.')

if __name__ == '__main__':
    ejecutar_sensor()
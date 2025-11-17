"""
Dashboard web completo para monitoreo IoT de Sevilla
"""

from flask import Flask, render_template, jsonify
from clickhouse_driver import Client
from datetime import datetime, timedelta
import json
from typing import Dict, List, Any
import os

app = Flask(__name__)

class SevillaDashboard:
    def __init__(self):
        self.clickhouse_client = Client(
        host=os.getenv('CLICKHOUSE_HOST', 'localhost'),
        port=int(os.getenv('CLICKHOUSE_PORT', '9000')),
        user=os.getenv('CLICKHOUSE_USER', 'admin'),
        password=os.getenv('CLICKHOUSE_PASSWORD', 'admin123'),
        database='sensors_db'
        )
    
    def get_latest_readings(self) -> List[Dict[str, Any]]:
        """
        Obtener últimas lecturas de cada sensor.
        """

        query = """
        SELECT sensor_id, ubicacion, temperatura, humedad, 
               calidad_aire, ruido_db, trafico_nivel, timestamp
        FROM sensor_data 
        WHERE timestamp > now() - INTERVAL 1 HOUR
        ORDER BY timestamp DESC 
        LIMIT 20
        """
        
        result = self.clickhouse_client.execute(query)
        return [
            {
                'sensor_id': row[0],
                'ubicacion': row[1], 
                'temperatura': row[2],
                'humedad': row[3],
                'calidad_aire': row[4],
                'ruido_db': row[5],
                'trafico_nivel': row[6],
                'timestamp': row[7].strftime('%H:%M:%S')
            }
            for row in result
        ]
    
    def get_zone_averages(self) -> Dict[str, Dict[str, float]]:
        """
        Promedios por zona en la última hora.
        """

        query = """
        SELECT ubicacion,
               round(avg(temperatura), 1) as temp_avg,
               round(avg(humedad), 1) as humedad_avg,
               round(avg(ruido_db), 1) as ruido_avg,
               round(avg(calidad_aire), 1) as aqi_avg,
               count() as lecturas
        FROM sensor_data 
        WHERE timestamp > now() - INTERVAL 1 HOUR
        GROUP BY ubicacion
        ORDER BY ubicacion
        """
        
        result = self.clickhouse_client.execute(query)
        return {
            row[0]: {
                'temperatura': row[1],
                'humedad': row[2], 
                'ruido': row[3],
                'aqi': row[4],
                'lecturas': row[5]
            }
            for row in result
        }
    
    def get_hourly_trends(self) -> Dict[str, List]:
        """
        Tendencias por hora en las últimas 6 horas.
        """

        query = """
        SELECT toStartOfHour(timestamp) as hour,
               ubicacion,
               round(avg(temperatura), 1) as temp_avg
        FROM sensor_data 
        WHERE timestamp > now() - INTERVAL 6 HOUR
        GROUP BY hour, ubicacion
        ORDER BY hour, ubicacion
        """
        
        result = self.clickhouse_client.execute(query)
        
        trends = {}
        for row in result:
            hour = row[0].strftime('%H:%M')
            ubicacion = row[1]
            temp = row[2]
            
            if ubicacion not in trends:
                trends[ubicacion] = {'hours': [], 'temps': []}
            
            trends[ubicacion]['hours'].append(hour)
            trends[ubicacion]['temps'].append(temp)
        
        return trends
    
    def get_stats_summary(self) -> Dict[str, Any]:
        """
        Estadísticas generales.
        """

        queries = {
            'total_readings': "SELECT count() FROM sensor_data",
            'active_sensors': "SELECT count(DISTINCT sensor_id) FROM sensor_data WHERE timestamp > now() - INTERVAL 10 MINUTE",
            'max_temp': "SELECT max(temperatura) FROM sensor_data WHERE timestamp > now() - INTERVAL 1 HOUR",
            'min_temp': "SELECT min(temperatura) FROM sensor_data WHERE timestamp > now() - INTERVAL 1 HOUR",
            'avg_temp': "SELECT round(avg(temperatura), 1) FROM sensor_data WHERE timestamp > now() - INTERVAL 1 HOUR"
        }
        
        stats = {}
        for key, query in queries.items():
            result = self.clickhouse_client.execute(query)
            stats[key] = result[0][0] if result and result[0] else 0
        
        return stats

dashboard = SevillaDashboard()

@app.route('/')
def index():
    """
    Página principal del dashboard.
    """

    try:
        stats = dashboard.get_stats_summary()
        zone_averages = dashboard.get_zone_averages()
        latest_readings = dashboard.get_latest_readings()
        
        return render_template('dashboard.html', 
                             stats=stats,
                             zones=zone_averages,
                             readings=latest_readings)
    except Exception as e:
        return f"Error: {e}", 500

@app.route('/api/live-data')
def live_data():
    """
    API para datos en tiempo real.
    """

    try:
        return jsonify({
            'stats': dashboard.get_stats_summary(),
            'zones': dashboard.get_zone_averages(),
            'latest': dashboard.get_latest_readings(),
            'trends': dashboard.get_hourly_trends(),
            'timestamp': datetime.now().strftime('%H:%M:%S')
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/health')
def health():
    """
    Health check.
    """
    
    return jsonify({'status': 'ok', 'timestamp': datetime.now().strftime('%H:%M:%S')})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
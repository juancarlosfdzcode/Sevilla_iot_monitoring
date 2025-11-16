🌆 Sevilla IoT Monitoring System
Sistema completo de monitoreo IoT en tiempo real para la ciudad de Sevilla, implementando una arquitectura de microservicios con streaming de datos y análisis en tiempo real.
🏗️ Arquitectura del Sistema
┌─────────────────┐    ┌──────────────┐    ┌────────────────┐    ┌─────────────────┐
│   Sensores IoT  │───▶│ Apache Kafka │───▶│ Kafka Consumer │───▶│ ClickHouse DB   │
│                 │    │              │    │                │    │                 │
│ • Centro        │    │ • Streaming  │    │ • Procesamiento│    │ • Analytics     │
│ • Triana        │    │ • Topics     │    │ • ETL          │    │ • Agregaciones  │
│ • Parque M.Luisa│    │ • Real-time  │    │ • Batch Insert │    │ • Time Series   │
│ • Nervión       │    │              │    │                │    │                 │
└─────────────────┘    └──────────────┘    └────────────────┘    └─────────────────┘
                                                                          │
                                                                          ▼
                                                                  ┌─────────────────┐
                                                                  │ Dashboard Web   │
                                                                  │                 │
                                                                  │ • Flask API     │
                                                                  │ • Real-time UI  │
                                                                  │ • Auto-refresh  │
                                                                  │ • Métricas      │
                                                                  └─────────────────┘
✨ Características Principales

🔌 4 Sensores IoT simulados con datos realistas de Sevilla
📡 Streaming en tiempo real con Apache Kafka
🗄️ Base de datos analítica ultra-rápida (ClickHouse)
📊 Dashboard web con visualización en tiempo real
🐳 Completamente containerizado con Docker
⚡ Auto-refresh cada 15 segundos
📈 Métricas por zona (Centro, Triana, Parque María Luisa, Nervión)
🔄 Procesamiento ETL automático con consumer Python

📊 Métricas Monitoreadas
MétricaDescripciónRango🌡️ TemperaturaTemperatura ambiente por zona15°C - 35°C💧 HumedadPorcentaje de humedad relativa40% - 80%🌬️ Calidad del AireÍndice de calidad del aire (AQI)1-4 (1=Bueno, 4=Malo)🔊 RuidoNivel de ruido ambiental40-75 dB🚗 TráficoNivel de tráfico vehicular1-5 (1=Bajo, 5=Alto)
📋 Prerequisitos

Docker >= 20.0 y Docker Compose >= 2.0
Python 3.10+ para desarrollo local
Git para clonar el repositorio
4GB RAM mínimo recomendado

Verificar prerequisitos:
bashdocker --version          # Debería mostrar >= 20.0
docker compose version    # Debería mostrar >= 2.0  
python3 --version         # Debería mostrar >= 3.10
🚀 Instalación Rápida
1. Clonar y preparar
bashgit clone https://github.com/tu-usuario/sevilla-iot-monitoring.git
cd sevilla-iot-monitoring
2. Ejecutar sistema completo
bash# Iniciar todos los servicios
docker compose up -d

# Inicializar base de datos (solo primera vez)
docker compose up clickhouse-init

# Ver estado de servicios
docker compose ps
3. Acceder al dashboard

📊 Dashboard Principal: http://localhost:5000
📡 API en tiempo real: http://localhost:5000/api/live-data
🔧 Health Check: http://localhost:5000/health

🛠️ Uso Detallado
Iniciar Sistema Paso a Paso
bash# 1. Iniciar infraestructura base
docker compose up -d zookeeper kafka clickhouse

# 2. Esperar que estén listos (30-60 segundos)
sleep 45

# 3. Verificar conectividad
curl http://localhost:8123/ping  # ClickHouse
docker exec kafka kafka-topics --bootstrap-server kafka:29092 --list  # Kafka

# 4. Inicializar base de datos
docker compose up clickhouse-init

# 5. Iniciar sensores
docker compose up -d sensors

# 6. Ver datos fluyendo en Kafka
docker exec kafka kafka-console-consumer --bootstrap-server kafka:29092 --topic sevilla-sensors --from-beginning
Ejecutar Consumer Local (Desarrollo)
bash# Instalar dependencias Python
pip3 install kafka-python clickhouse-driver flask

# Ejecutar consumer Kafka→ClickHouse
python src/kafka_to_clickhouse.py

# En otra terminal, ejecutar dashboard
python src/dashboard.py
Verificar Datos en ClickHouse
bash# Conectar al cliente ClickHouse
docker exec -it clickhouse clickhouse-client --user admin --password admin123

# Consultas útiles:
USE sensors_db;
SHOW TABLES;
SELECT COUNT(*) FROM sensor_data;
SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10;
SELECT ubicacion, round(avg(temperatura),1) FROM sensor_data GROUP BY ubicacion;
```

## 📁 Estructura del Proyecto
```
sevilla-iot-monitoring/
├── 📂 src/
│   ├── 🔌 sensor_kafka.py           # Sensores IoT con Kafka
│   ├── 🔗 kafka_to_clickhouse.py    # Consumer Kafka→ClickHouse  
│   ├── 📊 dashboard.py              # Dashboard web Flask
│   └── ⚙️ init_database.py          # Inicializador ClickHouse
├── 📂 templates/
│   └── 🎨 dashboard.html            # Template del dashboard
├── 📂 data/                         # Datos generados (git ignored)
├── 🐳 docker-compose.yml            # Orquestación de servicios
├── 🐳 Dockerfile                    # Imagen de sensores
├── 📋 requirements.txt              # Dependencias Python
├── 🚫 .gitignore                    # Archivos ignorados por Git
└── 📖 README.md                     # Este archivo
🔧 Configuración
Variables de Entorno
VariableDescripciónValor por defectoKAFKA_BROKERServidor Kafkakafka:29092TOPIC_NAMENombre del topicsevilla-sensorsSENSOR_INTERVALIntervalo entre lecturas10 segundosCLICKHOUSE_HOSTHost de ClickHouselocalhostCLICKHOUSE_USERUsuario ClickHouseadminCLICKHOUSE_PASSWORDPassword ClickHouseadmin123
Puertos Utilizados
ServicioPuertoDescripciónKafka9092Puerto principal para productores/consumidoresZookeeper2181Coordinación de KafkaClickHouse HTTP8123Interface HTTP de ClickHouseClickHouse Native9000Cliente nativo de ClickHouseDashboard5000Interface web del dashboard
📈 API Endpoints
Dashboard Web

GET / - Dashboard principal con visualización
GET /health - Health check del servicio
GET /api/live-data - Datos en tiempo real (JSON)

Ejemplo de respuesta API:
json{
  "stats": {
    "total_readings": 2450,
    "active_sensors": 4,
    "avg_temp": 24.2,
    "max_temp": 31.5,
    "min_temp": 18.7
  },
  "zones": {
    "Centro Histórico": {
      "temperatura": 25.1,
      "humedad": 68,
      "ruido": 58,
      "aqi": 2
    }
  },
  "timestamp": "14:30:15"
}
🐛 Troubleshooting
Problemas Comunes
❌ Error: "Connection refused" al iniciar
bash# Verificar que Docker está funcionando
docker ps

# Reiniciar servicios
docker compose down
docker compose up -d
❌ Error: "No module named kafka"
bash# Instalar dependencias locales
pip3 install -r requirements.txt
❌ Dashboard muestra error 500
bash# Verificar que ClickHouse está funcionando
curl http://localhost:8123/ping

# Ver logs del dashboard
docker compose logs sensors
❌ No se ven datos en ClickHouse
bash# Verificar que los sensores están enviando datos
docker compose logs sensors

# Verificar consumer
python src/kafka_to_clickhouse.py
Comandos de Diagnóstico
bash# Ver estado de todos los servicios
docker compose ps

# Ver logs de un servicio específico
docker compose logs -f sensors

# Verificar recursos del sistema
docker stats

# Limpiar todo y empezar de cero
docker compose down
docker system prune -f
docker compose up -d
🧪 Testing
Tests Básicos
bash# 1. Test de conectividad
curl http://localhost:8123/ping  # Debería devolver "Ok"
curl http://localhost:5000/health  # Debería devolver JSON con status ok

# 2. Test de datos
docker exec -it clickhouse clickhouse-client --user admin --password admin123 --query "SELECT COUNT(*) FROM sensors_db.sensor_data"

# 3. Test de Kafka
docker exec kafka kafka-console-consumer --bootstrap-server kafka:29092 --topic sevilla-sensors --max-messages 5
Datos de Prueba
El sistema genera automáticamente datos realistas:

Temperatura: Varía por zona (Centro más caluroso, Parque más fresco)
Humedad: Correlacionada con proximidad al río (Triana más húmedo)
Calidad del aire: Simulación realista para Sevilla
Ruido: Basado en características urbanas de cada zona
Tráfico: Patrones realistas por ubicación

🚀 Tecnologías Utilizadas
Backend

Python 3.11 - Lenguaje principal
Apache Kafka - Streaming de datos en tiempo real
ClickHouse - Base de datos analítica columnar
Flask - Framework web para dashboard

DevOps & Infraestructura

Docker & Docker Compose - Containerización
Zookeeper - Coordinación de Kafka

Frontend

HTML5 + CSS3 - Dashboard web responsive
JavaScript - Auto-refresh y interactividad

🚀 Despliegue en Producción
Consideraciones

Seguridad:

Cambiar contraseñas por defecto
Configurar SSL/TLS
Implementar autenticación


Escalabilidad:

Usar múltiples workers de Kafka
Configurar particiones apropiadas
Implementar load balancing


Monitoreo:

Añadir métricas de Prometheus
Configurar alertas
Logs estructurados



Variables de Entorno para Producción
bashexport KAFKA_BROKER="production-kafka:9092"
export CLICKHOUSE_HOST="production-clickhouse"
export CLICKHOUSE_PASSWORD="secure-password"
export FLASK_ENV="production"
🤝 Contribución

Fork del proyecto
Crear rama para feature (git checkout -b feature/nueva-funcionalidad)
Commit de cambios (git commit -am 'Añadir nueva funcionalidad')
Push a la rama (git push origin feature/nueva-funcionalidad)
Crear Pull Request

📄 Licencia
Este proyecto está bajo la Licencia MIT. Ver LICENSE para más detalles.
👨‍💻 Autor
Juan Carlos - Analytics Engineer

📧 Email: [tu-email@example.com]
💼 LinkedIn: [tu-perfil-linkedin]
🐙 GitHub: [tu-usuario-github]

🙏 Agradecimientos

Ciudad de Sevilla por la inspiración
Comunidad de Apache Kafka
Documentación de ClickHouse
Proyecto Flask


⭐ ¡Si te gusta este proyecto, dale una estrella! ⭐
🌆 Sevilla Smart City IoT - Monitoring the future, today!
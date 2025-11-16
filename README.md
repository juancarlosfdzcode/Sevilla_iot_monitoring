# 🌆 Sevilla IoT Monitoring System.

![Python](https://img.shields.io/badge/python-3.11-blue)
![Docker](https://img.shields.io/badge/docker-ready-blue)

En este proyecto se desarrolla un sistema completo de monitoreo de sensores IoT en tiempo real para la ciudad de Sevilla, implementando una arquitectura de microservicios con streaming de datos y análisis en tiempo real.

## 🏗️ Arquitectura del Sistema.


```
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
```


## ✨ Características Principales.

* 4 Sensores IoT simulados con datos realistas de Sevilla.
* Streaming en tiempo real con Apache Kafka.
* Base de datos analítica ultra-rápida (ClickHouse).
* Dashboard web con visualización en tiempo real.
* Completamente containerizado con Docker.
* Auto-refresh cada 15 segundos.
* Métricas por zona (Centro, Triana, Parque María Luisa, Nervión).
* Procesamiento ETL automático con consumer Python.
* Despliegue con un solo comando.

## 📊 Métricas Monitoreadas.

| Métrica | Descripción | Rango |
|----------|----------|----------|
| Temperatura | Temperatura ambiente por zonas | 15ºC - 35ºC |
| Humedad | Porcentaje de humedad relativa | 40% - 80% |
| Calidad del aire | Índice de calidad del aire (AQI) | 1-4 (1=Bueno, 4=Malo) |
| Ruido | Nivel de ruido ambiental | 40-75 dB |
| Tráfico | Nivel de tráfico vehicular | 1-5 (1=Bajo, 5=Alto) |

## 📋 Prerequisitos.

* Docker >= 20.0 y Docker Compose >= 2.0
* Git para clonar el repositorio
* 4GB RAM mínimo recomendado
* Puerto 5000 libre para el dashboard web

**Verificar prerequisitos:**

```bash
bashdocker --version          # Debería mostrar >= 20.0
docker compose version    # Debería mostrar >= 2.0
```

## 🚀 Instalación Ultra-Rápida.

**1. Clonar y ejecutar.**

```bash
# Clonar repositorio
git clone https://github.com/tu-usuario/sevilla-iot-monitoring.git
cd sevilla-iot-monitoring

# Ejecutar sistema completo con un solo comando
docker compose up -d

# Inicializar base de datos (solo primera vez)
docker compose up clickhouse-init
```

**2. ¡Listo! Acceder al dashboard.**

📊 Dashboard Principal: http://localhost:5000 \
📡 API en tiempo real: http://localhost:5000/api/live-data \
🔧 Health Check: http://localhost:5000/health


`⏱️ Nota: El sistema tarda ~3 minutos en estar completamente operativo debido a los tiempos de inicialización de Kafka.`

## 🎯 Servicios Incluidos.

El sistema incluye 6 servicios automáticos:

| Servicio | Descripción | Puerto |
|----------|----------|----------|
| sensors | 4 sensores IoT generando datos | - |
| kafka + zookeeper | Streaming de datos en tiempo real | 9092 |
| kafka-consumer | Procesamiento ETL automático | - |
| clickhouse | Base de datos analítica | 8123, 9000 |
| dashboard | Interfaz web con visualización | 5000 |
| clickhouse-init | Inicializador de BD (ejecuta una vez) | - |

## 🛠️ Comandos Útiles.

#### Gestión del Sistema.

```bash

# Ver estado de todos los servicios
docker compose ps

# Ver logs de un servicio específico
docker compose logs -f sensors
docker compose logs -f kafka-consumer
docker compose logs -f dashboard

# Reiniciar el sistema completo
docker compose down
docker compose up -d

# Parar sistema
docker compose down

# Limpiar todo (incluyendo datos)
docker compose down -v
docker system prune -f
```

#### Verificación de Datos.

```bash

# Ver datos en Kafka en tiempo real
docker exec kafka kafka-console-consumer --bootstrap-server kafka:29092 --topic sevilla-sensors --from-beginning

# Conectar a ClickHouse y consultar datos
docker exec -it clickhouse clickhouse-client --user admin --password admin123

# Dentro del cliente ClickHouse:
USE sensors_db;
SELECT COUNT(*) FROM sensor_data;
SELECT * FROM sensor_data ORDER BY timestamp DESC LIMIT 10;
```

## 📁 Estructura del Proyecto.

```
sevilla-iot-monitoring/
├── src/
│   ├── sensor_kafka.py           # Sensores IoT con Kafka
│   ├── kafka_to_clickhouse.py    # Consumer automático Kafka→ClickHouse  
│   ├── dashboard.py              # Dashboard web Flask
│   └── init_database.py          # Inicializador ClickHouse
├── templates/
│   └── dashboard.html            # Template del dashboard web
├── data/                         # Datos generados (git ignored)
├── docker-compose.yml            # Orquestación completa de servicios
├── Dockerfile                    # Imagen base de Python
├── requirements.txt              # Dependencias Python
├── .gitignore                    # Archivos ignorados por Git
└── README.md                     # Este archivo
```

## 🔧 Configuración.

#### Variables de Entorno (Automáticas).

| Variable | Descripción | Valor configurado |
| --- | --- | --- |
| KAFKA_BROKER | Servidor Kafka interno | kafka:29092 |
| TOPIC_NAME | Nombre del topic | sevilla-sensors |
| SENSOR_INTERVAL | Intervalo entre lecturas | 10 segundos |
| CLICKHOUSE_HOST | Host de ClickHouse interno | clickhouse |
| CLICKHOUSE_USER | Usuario ClickHouse | admin |
| CLICKHOUSE_PASSWORD | Password ClickHouse | admin123 |

#### Puertos Utilizados.

| Servicio | Puerto | Descripción |
| --- | --- | --- |
| Dashboard | 5000 | Interface web principal |
| Kafka | 9092 | Puerto para productores/consumidores |
| ClickHouse HTTP | 8123 | Interface HTTP de ClickHouse |
| ClickHouse Native | 9000 | Cliente nativo de ClickHouse |
| Zookeeper | 2181 | Coordinación de Kafka |

## 📈 API Endpoints.

##### Dashboard Web.

* `GET /` - Dashboard principal con visualización en tiempo real
* `GET /health` - Health check del servicio
* `GET /api/live-data` - Datos en tiempo real (JSON)

##### Ejemplo de respuesta API:

```
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
```

## 🐛 Troubleshooting.

##### Problemas Comunes.

**Error: "Connection refused" al iniciar.**
```bash
# Verificar que Docker está funcionando
docker ps

# Reiniciar servicios
docker compose down
docker compose up -d
```

**Dashboard no carga (Puerto 5000 en uso).**
```bash
# Verificar qué usa el puerto
lsof -i :5000

# Cerrar proceso que use el puerto y reiniciar
docker compose restart dashboard
```

**No se ven datos nuevos en el dashboard.**
```bash
# Verificar que todos los servicios están corriendo
docker compose ps

# Verificar logs del consumer
docker compose logs kafka-consumer

# Verificar datos en ClickHouse
docker exec -it clickhouse clickhouse-client --user admin --password admin123 --query "SELECT COUNT(*) FROM sensors_db.sensor_data"
```

**Error "NoBrokersAvailable".**
```bash
# Kafka necesita más tiempo para inicializar
# Esperar 3-5 minutos y verificar logs:
docker compose logs kafka
```

##### Comandos de Diagnóstico Completo.
```bash
# Diagnóstico automático del sistema
echo "=== ESTADO SERVICIOS ==="
docker compose ps

echo "=== DATOS EN KAFKA ==="
timeout 5s docker exec kafka kafka-console-consumer --bootstrap-server kafka:29092 --topic sevilla-sensors --from-beginning | wc -l

echo "=== DATOS EN CLICKHOUSE ==="
docker exec clickhouse clickhouse-client --user admin --password admin123 --query "SELECT COUNT(*) FROM sensors_db.sensor_data"

echo "=== ÚLTIMO REGISTRO ==="
docker exec clickhouse clickhouse-client --user admin --password admin123 --query "SELECT sensor_id, temperatura, timestamp FROM sensors_db.sensor_data ORDER BY timestamp DESC LIMIT 1"

echo "=== API DASHBOARD ==="
curl -s http://localhost:5000/health | jq
```

## 🧪 Testing.

##### Tests de Conectividad.

```bash
# 1. Test servicios básicos
curl http://localhost:8123/ping  # ClickHouse: debería devolver "Ok"
curl http://localhost:5000/health  # Dashboard: debería devolver JSON

# 2. Test de datos
docker exec kafka kafka-topics --list --bootstrap-server kafka:29092  # Debería mostrar "sevilla-sensors"

# 3. Test de flujo completo
curl http://localhost:5000/api/live-data | jq '.stats.total_readings'  # Debería mostrar número > 0
```

##### Datos de Prueba Automáticos.

El sistema genera automáticamente datos realistas para Sevilla:

* Centro Histórico: Temperaturas más altas, más ruido urbano.
* Triana: Humedad más alta (proximidad al río Guadalquivir).
* Parque María Luisa: Temperaturas más frescas, menos ruido.
* Nervión: Características urbanas intermedias.

## 🚀 Tecnologías Utilizadas.

##### Backend & Data Engineering.

* Python 3.11 - Lenguaje principal.
* Apache Kafka - Streaming de datos en tiempo real.
* ClickHouse - Base de datos analítica columnar.
* Flask - Framework web para dashboard y API.

##### DevOps & Infraestructura.

* Docker & Docker Compose - Containerización y orquestación.
* Zookeeper - Coordinación de Kafka.

##### Frontend & Visualización.

* HTML5 + CSS3 - Dashboard web responsive.
* JavaScript - Auto-refresh y interactividad en tiempo real.

## 🌟 Características Avanzadas.

* Escalable: Arquitectura preparada para múltiples instancias.
* Real-time: Dashboard se actualiza automáticamente cada 15 segundos.
* Enterprise-ready: Logs estructurados, health checks, métricas.
* Development-friendly: Sistema completo en desarrollo local.

## 🤝 Contribución.

* Fork del proyecto.
* Crear rama para feature (`git checkout -b feature/nueva-funcionalidad`).
* Commit de cambios (`git commit -am 'Añadir nueva funcionalidad'`).
* Push a la rama (`git push origin feature/nueva-funcionalidad`).
* Crear Pull Request-

## 👨‍💻 Autor.

Juan Carlos - Analytics Engineer.

📧 Email: juancarlosfdzgarcode@gmail.com \
💼 LinkedIn: [Mi Perfil.](https://www.linkedin.com/in/juan-carlos-fdz/) \
🐙 GitHub: [Mi GitHub.](https://github.com/juancarlosfdzcode)

##### ⭐ ¡Si te gusta este proyecto, dale una estrella! ⭐

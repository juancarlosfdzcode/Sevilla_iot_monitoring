CREATE DATABASE IF NOT EXISTS sensors_db;

USE sensors_db;

CREATE TABLE IF NOT EXISTS sensor_data (
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
TTL timestamp + INTERVAL 30 DAY;

CREATE TABLE IF NOT EXISTS sensor_hourly (
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
ORDER BY (hour, ubicacion);

CREATE MATERIALIZED VIEW IF NOT EXISTS sensor_hourly_mv
TO sensor_hourly
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
FROM sensor_data
GROUP BY hour, ubicacion;
# 🏭 IoT Sensor Dashboard

A **full-stack real-time IoT sensor monitoring** application built with **FastAPI** (Python) backend and **React.js** frontend. The backend subscribes to MQTT topics, stores sensor data in MySQL, and generates threshold-based alerts. The React frontend visualizes everything in a sleek, modern dashboard.

### Demo Video Link: https://drive.google.com/file/d/1gDFs_5Kh7spZcuSQ9HZFrQHRydQNyEEG/view?usp=sharing

---

## 📋 Table of Contents

- [Architecture](#architecture)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Setup & Installation](#setup--installation)
- [MQTT Topics & Thresholds](#mqtt-topics--thresholds)
- [API Documentation](#api-documentation)
- [Node-RED Integration](#node-red-integration)
- [Docker Deployment](#docker-deployment)
- [Hosting Exploration](#hosting-exploration)

---

## 🏗️ Architecture

```
┌──────────────┐     MQTT      ┌────────────────┐     SQL      ┌─────────┐
│  MQTT Broker │◄──────────────│  FastAPI        │─────────────►│  MySQL  │
│ (Mosquitto)  │  pub/sub      │  Backend        │  read/write  │   DB    │
└──────┬───────┘               └───────┬─────────┘              └─────────┘
       │                               │
       │ publish                       │ REST API
       │                               │
┌──────┴───────┐               ┌───────┴─────────┐
│  Simulator / │               │  React.js       │
│  Node-RED    │               │  Frontend       │
└──────────────┘               └─────────────────┘
```

### Data Flow
1. **Sensor Simulator / Node-RED** publishes JSON messages to MQTT topics
2. **FastAPI Backend** subscribes to all topics via `paho-mqtt`
3. Each message is **parsed**, **validated against thresholds**, and **stored** in MySQL
4. If any parameter breaches a threshold → an **alert** is created and stored
5. **React Frontend** fetches data via REST APIs and displays it in real-time

---

## ✨ Features

### Backend
- ✅ FastAPI with auto-generated Swagger docs (`/docs`)
- ✅ MQTT subscriber on **8 sensor topics** (runs in background thread)
- ✅ **5 sensor parameters**: Temperature, Humidity, Voltage, Current, Pressure
- ✅ Threshold validation with **warning/critical** severity levels
- ✅ MySQL storage with SQLAlchemy ORM
- ✅ Paginated APIs with filters (topic, time range, severity)
- ✅ CORS enabled for frontend integration
- ✅ Clean, modular FastAPI architecture

### Frontend
- ✅ **Dashboard**: Live stats cards, sensor readings grid, recent alerts timeline
- ✅ **Alerts Page**: Paginated table with severity badges, violated param highlighting
- ✅ **Raw Data Page**: Tabular view with pagination and topic filter
- ✅ Threshold breach values highlighted in **red**
- ✅ Auto-refresh every 5 seconds
- ✅ Responsive design (desktop + tablet + mobile)
- ✅ Premium dark theme with glassmorphism UI

### DevOps
- ✅ Docker Compose (MySQL + Mosquitto + Backend + Simulator)
- ✅ Node-RED flow export for reference
- ✅ Python MQTT simulator (alternative to Node-RED)

---

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | Python 3.11, FastAPI, Uvicorn |
| MQTT | Paho-MQTT (client), Eclipse Mosquitto (broker) |
| Database | MySQL 8.0, SQLAlchemy ORM, PyMySQL |
| Frontend | React 18, Vite, React Router 6, Axios |
| Icons | Lucide React |
| Containerization | Docker, Docker Compose |

---

## 📁 Project Structure

```
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI app entry point
│   │   ├── config.py            # Env vars, thresholds, MQTT topics
│   │   ├── database.py          # SQLAlchemy engine & session
│   │   ├── models.py            # ORM models (SensorData, Alert)
│   │   ├── schemas.py           # Pydantic request/response schemas
│   │   ├── mqtt_client.py       # MQTT subscriber + threshold logic
│   │   └── routers/
│   │       ├── sensor_data.py   # /api/sensor-data endpoints
│   │       └── alerts.py        # /api/alerts endpoints
│   ├── simulator/
│   │   └── mqtt_simulator.py    # Test data generator
│   ├── requirements.txt
│   ├── Dockerfile
│   └── .env
├── frontend/
│   ├── src/
│   │   ├── pages/
│   │   │   ├── Dashboard.jsx    # Main dashboard with live stats
│   │   │   ├── Alerts.jsx       # Alert listing & filters
│   │   │   └── RawData.jsx      # Raw sensor data table
│   │   ├── services/
│   │   │   └── api.js           # Axios API service layer
│   │   ├── App.jsx              # Root component with routing
│   │   ├── main.jsx             # Entry point
│   │   └── index.css            # Global styles (dark theme)
│   ├── package.json
│   ├── vite.config.js
│   └── index.html
├── mosquitto/config/
│   └── mosquitto.conf           # Broker configuration
├── docker-compose.yml
├── node-red-flows.json          # Node-RED flow export
└── README.md
```

---

## 🚀 Setup & Installation

### Option 1: Docker (Recommended)

```bash
# Start all services (MySQL, Mosquitto, Backend)
docker-compose up -d

# Start the simulator to generate test data
docker-compose --profile simulator up -d

# Backend API will be at: http://localhost:8000
# Swagger docs: http://localhost:8000/docs
```

### Option 2: Manual Setup

#### Prerequisites
- Python 3.11+
- Node.js 18+
- MySQL 8.0
- Mosquitto MQTT Broker

#### Backend
```bash
cd backend

# Create virtual environment
python -m venv venv
venv\Scripts\activate       # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Configure .env file (update DB credentials if needed)

# Start the backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

#### Frontend
```bash
cd frontend
npm install
npm run dev
# Opens at http://localhost:5173
```

#### Simulator
```bash
cd backend
python -m simulator.mqtt_simulator
```

---

## 📡 MQTT Topics & Thresholds

### Subscribed Topics (8)
| Topic | Device |
|-------|--------|
| `sensor/plant1/boiler` | Boiler Unit |
| `sensor/plant1/turbine` | Turbine |
| `sensor/plant2/compressor` | Compressor |
| `sensor/plant2/generator` | Generator |
| `sensor/plant3/hvac` | HVAC System |
| `sensor/plant3/motor` | Motor |
| `sensor/warehouse/cold_storage` | Cold Storage |
| `sensor/warehouse/conveyor` | Conveyor Belt |

### Threshold Configuration
| Parameter | Min | Max | Unit |
|-----------|-----|-----|------|
| Temperature | -10 | 60 | °C |
| Humidity | 10 | 90 | % |
| Voltage | 180 | 260 | V |
| Current | 0 | 30 | A |
| Pressure | 950 | 1050 | hPa |

### Alert Severity Logic
- **Warning**: Value is outside the min/max range
- **Critical**: Value is > 20% beyond the range boundary

---

## 📖 API Documentation

Full Swagger UI available at `http://localhost:8000/docs`

### Sensor Data Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/sensor-data` | Paginated raw data (filters: topic, time) |
| GET | `/api/sensor-data/latest` | Latest reading per topic |
| GET | `/api/sensor-data/stats` | Aggregate statistics |
| GET | `/api/sensor-data/thresholds` | Current threshold config |
| GET | `/api/sensor-data/topics` | List of active topics |

### Alert Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/alerts` | Paginated alerts (filters: topic, severity, time) |
| GET | `/api/alerts/recent` | Last N alerts |
| GET | `/api/alerts/count` | Count by severity |

### Sample Response - Sensor Data
```json
{
  "id": 42,
  "topic": "sensor/plant1/boiler",
  "temperature": 45.23,
  "humidity": 62.10,
  "voltage": 220.50,
  "current": 15.80,
  "pressure": 1013.25,
  "timestamp": "2026-02-22T10:30:00"
}
```

### Sample Response - Alert
```json
{
  "id": 7,
  "sensor_data_id": 42,
  "topic": "sensor/plant1/boiler",
  "severity": "critical",
  "violated_keys": ["temperature", "voltage"],
  "actual_values": {"temperature": 75.2, "voltage": 280.5},
  "threshold_values": {
    "temperature": {"min": -10, "max": 60},
    "voltage": {"min": 180, "max": 260}
  },
  "timestamp": "2026-02-22T10:30:00"
}
```

---

## 🔴 Node-RED Integration

A sample Node-RED flow is included in `node-red-flows.json`. To use:

1. Install Node-RED: `npm install -g node-red`
2. Start: `node-red`
3. Open `http://localhost:1880`
4. Import the flow via Menu → Import → `node-red-flows.json`
5. Configure the MQTT broker node to point to your Mosquitto instance
6. Deploy the flow

The flow generates random sensor data (with ~20% threshold breaches) and publishes to the configured MQTT topics every 3 seconds.

---

## 🐳 Docker Deployment

### Services
| Service | Port | Description |
|---------|------|-------------|
| MySQL | 3306 | Database |
| Mosquitto | 1883 (MQTT), 9001 (WS) | MQTT Broker |
| Backend | 8000 | FastAPI API |
| Simulator | — | MQTT data generator (optional) |

### Commands
```bash
# Start core services
docker-compose up -d

# Start with simulator
docker-compose --profile simulator up -d

# View logs
docker-compose logs -f backend

# Stop all
docker-compose down

# Remove volumes (reset data)
docker-compose down -v
```

---

## 🌐 Hosting Exploration

### Backend Hosting Options
| Platform | Type | Notes |
|----------|------|-------|
| **AWS EC2** | VM | Full control, run Docker Compose |
| **AWS ECS/Fargate** | Container | Managed containers, auto-scaling |
| **Railway** | PaaS | Easy Docker deploy, built-in MySQL |
| **Render** | PaaS | Free tier, Docker support |
| **DigitalOcean** | VM/App Platform | Affordable, Docker support |

### Frontend Hosting Options
| Platform | Type | Notes |
|----------|------|-------|
| **Vercel** | Static/SSR | Best for React, free tier |
| **Netlify** | Static | Easy deploy, CDN |
| **AWS S3 + CloudFront** | Static | Enterprise-grade CDN |
| **GitHub Pages** | Static | Free, direct from repo |

### MQTT Broker Hosting
| Platform | Type | Notes |
|----------|------|-------|
| **HiveMQ Cloud** | Managed | Free tier, 100 connections |
| **CloudMQTT** | Managed | Easy setup |
| **AWS IoT Core** | Managed | Enterprise MQTT |
| **Self-hosted** | Mosquitto on EC2 | Full control |

### Database Hosting
| Platform | Notes |
|----------|-------|
| **PlanetScale** | Serverless MySQL, free tier |
| **AWS RDS** | Managed MySQL |
| **Railway** | Built-in MySQL |
| **Aiven** | Managed, free tier |

---

## 🧠 Logic & Architecture Decisions

1. **Background MQTT Thread**: The MQTT subscriber runs on a daemon thread managed by FastAPI's lifespan events, ensuring it starts/stops with the app.

2. **Threshold Validation**: Every incoming message is validated in real-time. Severity is computed based on how far outside the range the value falls (>20% beyond = critical).

3. **Separate Alert Table**: Alerts store violated keys, actual values, AND threshold values as JSON — enabling full forensic analysis on the frontend.

4. **API Proxy**: Vite dev server proxies `/api` requests to the backend, avoiding CORS issues during development.

5. **Auto-refresh**: Frontend polls every 5 seconds for new data using `setInterval` with React hooks.

---

## 📝 License

MIT License — feel free to use for educational purposes.

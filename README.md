# ⚙️ Automatic Fault Detection and Diagnostic (AFDD) System

This project simulates an end-to-end fault detection system using:

- 🐍 **Django** (Backend + ORM)
- 🐇 **RabbitMQ** (Message Broker)
- 🧪 **Supabase** (PostgreSQL DB with real-time subscriptions)
- ⚛️ **React** (Frontend)
- 🐳 **Docker Compose** (Service orchestration)
- 🤖 **Python agents** (for simulating and detecting faults)

> 📁 `IoT_faultDetection/` — Backend code  
> 📁 `fault_detection_management/` — Frontend code

---

## 🚀 Quick Start with Docker Compose

### 🔧 Prerequisites

- [Docker](https://www.docker.com/)
- [Docker Compose](https://docs.docker.com/compose/)

---

### 🏁 Step 1: Add Environment Variables

Create a `.env` file inside the `IoT_faultDetection/` folder using the credentials provided to you.

---

### 🏗️ Step 2: Build and Launch the System

Run the following command from the project root:

```bash
docker-compose up --build
```

This will start:
- 🐍 Django app (backend + REST API). When running, all active fault alerts are deleted to demonstrate the real-time notificaton since delete and update function is not done yet
- 🐇 RabbitMQ (management UI at http://localhost:15672)
- ⚛️ React frontend (at http://localhost:3000). However sometimes, refresh needs to be done when Django isn't started fully. Will be solved in future work
- 🤖 Python agents (sensor_simulator.py and worker.py) Current, the threshold for device can be set in work.py. In the future work. endpoints would be created

## 🧪 How It Works

1. Sensor Simulator generates random IoT data (temperature, humidity, CO₂).
2. Worker compares this data with threshold limits.
3. If a fault is detected:
     - It stores it in the PostgreSQL DB using Django ORM.
     - Supabase triggers a real-time notification.
4. React App listens for real-time changes and displays fault alerts instantly.

## ✅ Available API Endpoints (via Django)
GET /fault-detection/active-alarms/
→ List of all active alarms

GET /fault-detection/active-fault-alarms/
→ List of active alarms with detected faults

## 📬 RabbitMQ UI
Access RabbitMQ Management Interface:
http://localhost:15672  
Username: guest  
Password: guest

## 🔮 Future Enhancements
- ✅ Alarm resolution and acknowledgment APIs
- 🔐 User login system (Authentication)
- ⚙️ Per-room or per-device threshold configuration via UI
- 📊 Dashboard to view historical fault trends

## 🧹 Cleanup

To stop and remove all containers:

```bash
docker-compose down
```

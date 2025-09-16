# Smart Sentry

**Real-Time, Phase-Aware Anomaly Detection for Industrial Assets**

A real-time monitoring system designed for the Baker Hughes Hackathon 2025. Smart Sentry provides an end-to-end solution for ingesting, analyzing, and visualizing sensor data from industrial assets, with a specialized focus on accurately detecting anomalies across all operational phases.

---
## Table of Contents

* [Project Overview](#project-overview)
* [Key Features](#key-features)
* [System Architecture](#system-architecture)
* [Data Workflow](#data-workflow)
* [Technology Stack](#technology-stack)
* [Installation and Setup Guide](#installation-and-setup-guide)
* [Edge Deployment Strategy](#edge-deployment-strategy)
* [Project Structure](#project-structure)
* [Team](#team)

---
## Project Overview

In modern industries, while most anomaly detection systems focus on steady-state operations, critical failures often emerge during transitional phases like equipment startup or shutdown. These phases are characterized by transient but normal spikes in sensor readings, which can lead to a high rate of false positive alerts. This "alarm fatigue" makes it difficult for operators to identify genuine issues.

**Smart Sentry** solves this problem by implementing a phase-aware monitoring system. It learns the unique behavioral patterns for each operational phase—startup, steady-state, and shutdown—independently. By applying the correct machine learning model for the asset's current context, the system can accurately detect true anomalies while significantly reducing false positives, especially during transient states.

---
## Key Features

* **Real-Time Data Streaming**: Simulates high-frequency sensor data using an MQTT message bus to mimic a live industrial asset.
* **Dynamic Phase Identification**: Automatically detects the asset's current operational state in real-time.
* **Phase-Specific Machine Learning**: Utilizes separate `IsolationForest` models for each operational phase to ensure high detection accuracy.
* **Root Cause Analysis**: Enriches alerts with a predicted failure type to provide more actionable insights.
* **Live Interactive Dashboard**: A Grafana dashboard visualizes all sensor data, the current operational phase, and a running list of anomalies.
* **Anomaly Annotations**: Automatically overlays failure events on sensor graphs for immediate visual correlation between alerts and data.
* **Network-Wide Accessibility**: A user-friendly hostname (`http://smartsentry.local`) provides access to the dashboard from any device on the local network.

---
## System Architecture

The system is built on a decoupled, event-driven architecture designed for scalability and resilience.
Of course. Here is the complete code for your README.md file.

[Simulator] -> [MQTT Broker] -> [Real-Time Engine] -> [MQTT Broker] -> [Data Logger] -> [PostgreSQL] -> [Grafana]
|                     |
(Phase ID & Anomaly)   (Alerts)

* **Communication Layer (MQTT)**: A central Mosquitto message broker acts as the system's nervous system, allowing all components to communicate asynchronously.
* **Intelligence Layer (Python)**: A suite of Python scripts forms the brain of the operation, handling data simulation, real-time analysis, and data logging.
* **Persistence Layer (PostgreSQL)**: A PostgreSQL database serves as the system's long-term memory, storing all time-series data and generated alerts.
* **Presentation Layer (Grafana & Nginx)**: A Grafana dashboard provides the user interface, made accessible on the standard web port 80 via an Nginx reverse proxy.

---
## Data Workflow

1.  **Ingestion**: The **Simulator** publishes a sensor reading to a raw data topic on the MQTT broker.
2.  **Analysis**: The **Real-Time Engine** subscribes to this topic and immediately:
    * Identifies the operational **phase** of the asset.
    * Selects the correct ML model for that phase to detect **anomalies**.
    * Predicts a potential **failure type** if an anomaly is found.
3.  **Enrichment & Alerting**: The engine publishes the enriched data (with phase) and any detailed alerts to new, separate topics on the MQTT broker.
4.  **Persistence**: The **Data Logger** subscribes to these topics and saves the information into the appropriate tables in the **PostgreSQL** database.
5.  **Visualization**: The **Grafana** dashboard, which continuously queries the database, instantly reflects the new data and alerts.

---
## Technology Stack

| Category         | Technology                               |
| ---------------- | ---------------------------------------- |
| **Backend** | Python, scikit-learn, Pandas             |
| **Messaging** | MQTT (Mosquitto)                         |
| **Database** | PostgreSQL                               |
| **Dashboard** | Grafana                                  |
| **Web Server** | Nginx (as Reverse Proxy)                 |
| **Deployment** | Raspberry Pi (Ubuntu Server)             |

---
## Installation and Setup Guide

This guide details the process of setting up the Smart Sentry application on a compatible system.

#### **Prerequisites**
* **Hardware**: A Raspberry Pi (Model 3B+ or newer) is recommended.
* **Operating System**: Ubuntu Server 22.04 LTS or a similar Debian-based distribution.
* **Initial Setup**: An active internet connection and `sudo` privileges.

#### **Phase 1: Core Service Installation**

1.  **Update System and Install Tools**:
    ```bash
    sudo apt update && sudo apt upgrade -y
    sudo apt install -y python3 python3-pip python3-venv git
    ```

2.  **Install and Configure Mosquitto (MQTT Broker)**:
    ```bash
    sudo apt install -y mosquitto mosquitto-clients
    sudo systemctl enable --now mosquitto.service
    ```

3.  **Install and Configure PostgreSQL**:
    ```bash
    sudo apt install -y postgresql postgresql-contrib
    sudo systemctl enable --now postgresql.service
    # Create the database and user
    sudo -u postgres psql -c "CREATE DATABASE asset_data;"
    sudo -u postgres psql -c "CREATE USER sentry_user WITH PASSWORD 'your_password';"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE asset_data TO sentry_user;"
    ```

4.  **Install and Configure Grafana**:
    ```bash
    sudo apt install -y apt-transport-https software-properties-common wget
    sudo mkdir -p /etc/apt/keyrings/
    wget -q -O - [https://apt.grafana.com/gpg.key](https://apt.grafana.com/gpg.key) | gpg --dearmor | sudo tee /etc/apt/keyrings/grafana.gpg > /dev/null
    echo "deb [signed-by=/etc/apt/keyrings/grafana.gpg] [https://apt.grafana.com](https://apt.grafana.com) stable main" | sudo tee /etc/apt/sources.list.d/grafana.list
    sudo apt update
    sudo apt install -y grafana
    sudo systemctl enable --now grafana-server.service
    ```

#### **Phase 2: Application Setup**

1.  **Clone the Repository**:
    ```bash
    git clone [your-repository-url]
    cd [repository-name]
    ```

2.  **Set Up Python Environment**:
    ```bash
    python3 -m venv env
    source env/bin/activate
    pip install -r requirements.txt
    ```

3.  **Set Up Database Schema**:
    Log in to PostgreSQL and create the necessary tables.
    ```bash
    sudo -u postgres psql -d asset_data
    ```
    Run the following SQL commands:
    ```sql
    CREATE TABLE sensor_readings (
        id SERIAL PRIMARY KEY, timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(), unit_number INT,
        time_in_cycles INT, phase VARCHAR(50), setting_1 FLOAT, setting_2 FLOAT, setting_3 FLOAT,
        sensor_1 FLOAT, sensor_2 FLOAT, sensor_3 FLOAT, sensor_4 FLOAT, sensor_5 FLOAT, sensor_6 FLOAT,
        sensor_7 FLOAT, sensor_8 FLOAT, sensor_9 FLOAT, sensor_10 FLOAT, sensor_11 FLOAT, sensor_12 FLOAT,
        sensor_13 FLOAT, sensor_14 FLOAT, sensor_15 FLOAT, sensor_16 FLOAT, sensor_17 FLOAT, sensor_18 FLOAT,
        sensor_19 FLOAT, sensor_20 FLOAT, sensor_21 FLOAT
    );

    CREATE TABLE alerts (
        id SERIAL PRIMARY KEY, timestamp TIMESTAMPTZ NOT NULL DEFAULT NOW(), unit_number INT,
        time_in_cycles INT, phase VARCHAR(50), failure_type VARCHAR(100)
    );

    GRANT ALL PRIVILEGES ON TABLE sensor_readings, alerts TO sentry_user;
    GRANT USAGE ON SEQUENCE sensor_readings_id_seq, alerts_id_seq TO sentry_user;
    \q
    ```

4.  **Run the Application**:
    Open separate terminal sessions for each script and activate the virtual environment in each.
    ```bash
    # Terminal 1:
    python simulator.py

    # Terminal 2:
    python data_logger.py

    # Terminal 3:
    python real_time_engine.py
    ```

5.  **Train the Models**:
    After allowing the system to run and collect some data, run the training script:
    ```bash
    python train_models.py
    ```
    Restart the `real_time_engine.py` script to load the new models.

---
## Edge Deployment Strategy

The Smart Sentry system was architected to meet the specific challenges of edge deployment, focusing on limited resources and unreliable connectivity.

* **On-Device Intelligence**: The entire data processing workflow runs directly on the edge device. This minimizes latency, as data does not require a round trip to a cloud server for analysis, and ensures operational continuity even if the external network connection is lost.
* **Lightweight Machine Learning**: The system utilizes `IsolationForest`, a computationally efficient algorithm with a small memory footprint, making it ideal for devices with limited computing resources. For more complex tasks, models can be optimized using frameworks like ONNX or TensorFlow Lite to maintain performance on the edge.
* **Bandwidth Management**: The high-frequency raw sensor data is processed locally. Only critical, high-value information—such as confirmed anomaly alerts or down-sampled summary statistics—is transmitted over the network. This approach drastically reduces bandwidth consumption, which is crucial for environments with unreliable or high-cost connectivity.

---
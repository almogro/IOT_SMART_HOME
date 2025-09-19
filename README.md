# Elderly Care Smart Home System

A comprehensive IoT-based smart home system designed specifically for elderly care, featuring fall detection, health monitoring, emergency response, and medication management.

## 🏠 Project Overview

This system addresses the critical need for elderly care by providing:
- **Fall Detection**: Real-time monitoring with emergency response
- **Health Monitoring**: Continuous vital signs tracking
- **Emergency Response**: Immediate family and emergency service notifications
- **Smart Lighting**: Automatic lighting based on movement and emergencies
- **Medication Management**: Automated reminders and compliance tracking

## 🚀 Features

### Safety & Emergency Features
- **Fall Detection Sensor**: Accelerometer-based fall detection with emergency alerts
- **Emergency Button**: Manual emergency trigger with immediate response
- **Emergency Lighting**: Automatic activation during emergencies
- **Family Notifications**: Real-time alerts to family members

### Health Monitoring
- **Vital Signs Tracking**: Heart rate, blood pressure, temperature, oxygen saturation
- **Health Alerts**: Automatic warnings for abnormal readings
- **Medical Integration**: Direct alerts to healthcare providers

### Smart Home Controls
- **Motion-Activated Lighting**: Automatic lights based on movement
- **Room-Specific Controls**: Individual control for each room
- **Emergency Mode**: All lights activate during emergencies

### Medication Management
- **Automated Reminders**: Scheduled medication notifications
- **Compliance Tracking**: Monitor medication adherence
- **Missed Dose Alerts**: Immediate notifications for missed medications

## 🛠️ Technical Architecture

### Components
1. **Fall Detection Sensor** (`fall_detection_sensor.py`)
2. **Health Monitor** (`health_monitor.py`)
3. **Emergency Button** (`emergency_button.py`)
4. **Smart Lighting Controller** (`smart_lighting_controller.py`)
5. **Medication Reminder System** (`medication_reminder.py`)
6. **Data Manager** (`manager.py`)
7. **Main GUI Application** (`gui.py`)

### Technology Stack
- **MQTT**: Message queuing for IoT communication
- **SQLite**: Local database for data storage
- **PyQt5**: GUI framework
- **Python**: Core programming language
- **Cloud Integration**: Ready for cloud database integration

## 📋 Requirements

### Software Requirements
- Python 3.7+
- PyQt5
- paho-mqtt
- pandas
- sqlite3
- pyqtgraph
- matplotlib
- icecream

### Hardware Requirements
- Computer with Python environment
- MQTT broker (HiveMQ, Mosquitto, or local)
- Internet connection for MQTT communication

## 🚀 Installation & Setup

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd ElderlyCare-SmartHome
   ```

2. **Install dependencies**:
   ```bash
   pip install PyQt5 paho-mqtt pandas pyqtgraph matplotlib icecream
   ```

3. **Initialize the database**:
   ```bash
   python data_acq.py
   ```

4. **Start the system**:
   ```bash
   python start_elderly_care_system.py
   ```

## 🎮 Usage

### Starting the System
1. Run the startup script: `python start_elderly_care_system.py`
2. This will start all emulators and the main GUI
3. Connect to the MQTT broker using the GUI
4. Monitor the system through the dashboard

### Individual Emulators
You can also run individual emulators separately:
- `python fall_detection_sensor.py`
- `python health_monitor.py`
- `python emergency_button.py`
- `python smart_lighting_controller.py`
- `python medication_reminder.py`

### Main Applications
- `python manager.py` - Data manager and MQTT broker
- `python gui.py` - Main GUI dashboard

## 📊 Database Schema

The system uses SQLite with the following tables:
- `sensor_data`: All sensor readings and device data
- `elderly_devices`: Device configuration and status
- `emergency_logs`: Emergency events and responses
- `health_metrics`: Health monitoring data
- `medication_logs`: Medication compliance tracking

## 🔧 Configuration

Edit `init.py` to configure:
- MQTT broker settings
- Health monitoring thresholds
- Emergency response settings
- Database configuration

## 📱 GUI Features

### Main Dashboard
- **Connection Status**: MQTT broker connection
- **Emergency Status**: Real-time emergency monitoring
- **Health Monitoring**: Vital signs display
- **Smart Controls**: Lighting and device control
- **Medication Management**: Schedule and compliance tracking
- **System Alerts**: All notifications and warnings

## 🚨 Emergency Response

The system provides multiple layers of emergency response:

1. **Automatic Detection**: Fall detection and health monitoring
2. **Manual Trigger**: Emergency button for immediate help
3. **Family Notifications**: Real-time alerts to family members
4. **Emergency Services**: Direct integration with emergency services
5. **Smart Home Response**: Automatic lighting and environmental controls

## 📈 Monitoring & Analytics

- Real-time health metrics tracking
- Emergency response time monitoring
- Medication compliance analytics
- System performance metrics
- Historical data analysis

## 🔒 Security & Privacy

- Local data storage with SQLite
- Secure MQTT communication
- Privacy-focused design
- Family-controlled access

## 🎯 Course Requirements Compliance

This project fulfills all course requirements:

### Required Components (30 points)
- ✅ **3+ Emulator Types** (6 points): Fall detection sensor, health monitor, emergency button, smart lighting controller, medication reminder
- ✅ **Data Manager App** (8 points): MQTT data collection, database storage, message processing, alarm system
- ✅ **Main GUI App** (10 points): Real-time data display, control interface, status monitoring, alert system
- ✅ **Local/Cloud DB** (3 points): SQLite database with cloud integration capability

### Additional Features
- **Emergency Response System**: Comprehensive safety features
- **Health Monitoring**: Advanced vital signs tracking
- **Smart Home Integration**: Automated environmental controls
- **Medication Management**: Compliance tracking and reminders

## 📞 Support

For technical support or questions about the system, please refer to the course materials or contact the development team.

## 📄 License

This project is developed for educational purposes as part of the IoT course curriculum.

---

**Note**: This system is designed for educational and demonstration purposes. For real-world deployment, additional safety measures, medical device certifications, and professional healthcare integration would be required.

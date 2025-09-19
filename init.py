# Elderly Care Smart Home Configuration Module

import socket

# MQTT Broker Configuration
nb = 1  # 0- HIT-"139.162.222.115", 1 - open HiveMQ - broker.hivemq.com
brokers = [str(socket.gethostbyname('vmm1.saaintertrade.com')), 
           str(socket.gethostbyname('broker.hivemq.com')),
           "test.mosquitto.org"]
ports = ['80', '1883', '1883']
usernames = ['', '', '']
passwords = ['', '', '']

broker_ip = brokers[nb]
broker_port = ports[nb]
username = usernames[nb]
password = passwords[nb]
conn_time = 0  # 0 stands for endless

# Common topic prefix for elderly care system
comm_topic = 'elderly_care/'

# Database configuration
db_name = 'data/elderly_care_home.db'
db_init = False  # Set to True if we need to reinitialize database

# Health monitoring thresholds
HEART_RATE_MIN = 50
HEART_RATE_MAX = 120
BLOOD_PRESSURE_SYSTOLIC_MAX = 180
BLOOD_PRESSURE_DIASTOLIC_MAX = 110
TEMPERATURE_MIN = 35.0
TEMPERATURE_MAX = 39.0

# Fall detection thresholds
FALL_ACCELERATION_THRESHOLD = 2.5  # g-force
FALL_VELOCITY_THRESHOLD = 0.5
NO_MOVEMENT_THRESHOLD = 30  # minutes

# Emergency response settings
EMERGENCY_RESPONSE_TIME = 5  # seconds
FAMILY_NOTIFICATION_DELAY = 10  # seconds

# Update intervals (in seconds)
HEALTH_MONITOR_INTERVAL = 30
FALL_DETECTION_INTERVAL = 1
ENVIRONMENTAL_INTERVAL = 60
MEDICATION_REMINDER_INTERVAL = 3600  # 1 hour

# Device status messages
msg_system = ['normal', 'warning', 'emergency', 'no_issue']
wait_time = 5

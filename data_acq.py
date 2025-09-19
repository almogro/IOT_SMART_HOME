# Data Acquisition Module for Elderly Care Smart Home
import csv
import os
import pandas as pd 
from init import *
import sqlite3
from sqlite3 import Error
from datetime import datetime
import time as tm
from icecream import ic as ic2
import matplotlib.pyplot as plt
import random

def time_format():
    return f'{datetime.now()}  data acq|> '

ic2.configureOutput(prefix=time_format)

def create_connection(db_file=db_name):
    """ create a database connection to the SQLite database
        specified by db_file
    :param db_file: database file
    :return: Connection object or None
    """
    conn = None
    try:
        # Create data directory if it doesn't exist
        os.makedirs(os.path.dirname(db_file), exist_ok=True)
        conn = sqlite3.connect(db_file)
        pp = ('Connected to version: ' + sqlite3.version)
        ic2(pp)
        return conn
    except Error as e:
        ic2(e)

    return conn

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        ic2(e)

def init_db(database):
    # Database tables for elderly care system
    tables = [
    """ CREATE TABLE IF NOT EXISTS `sensor_data` (
        `id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `device_name` TEXT NOT NULL,
        `device_type` TEXT NOT NULL,
        `timestamp` TEXT NOT NULL,
        `value` TEXT NOT NULL,
        `status` TEXT,
        `location` TEXT,
        `alert_level` TEXT DEFAULT 'normal'
    );""",
    """CREATE TABLE IF NOT EXISTS `elderly_devices` (
        `device_id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `device_name` TEXT NOT NULL UNIQUE,
        `device_type` TEXT NOT NULL,
        `status` TEXT,
        `location` TEXT,
        `last_updated` TEXT NOT NULL,
        `update_interval` INTEGER NOT NULL,
        `enabled` INTEGER,
        `alert_threshold` TEXT,
        `emergency_contact` TEXT,
        `pub_topic` TEXT NOT NULL,
        `sub_topic` TEXT NOT NULL,
        `special_notes` TEXT
    );""",
    """CREATE TABLE IF NOT EXISTS `emergency_logs` (
        `log_id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `timestamp` TEXT NOT NULL,
        `device_name` TEXT NOT NULL,
        `emergency_type` TEXT NOT NULL,
        `severity` TEXT NOT NULL,
        `message` TEXT NOT NULL,
        `response_time` REAL,
        `resolved` INTEGER DEFAULT 0,
        `family_notified` INTEGER DEFAULT 0
    );""",
    """CREATE TABLE IF NOT EXISTS `health_metrics` (
        `metric_id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `timestamp` TEXT NOT NULL,
        `heart_rate` INTEGER,
        `blood_pressure_systolic` INTEGER,
        `blood_pressure_diastolic` INTEGER,
        `temperature` REAL,
        `oxygen_saturation` INTEGER,
        `alert_level` TEXT DEFAULT 'normal'
    );""",
    """CREATE TABLE IF NOT EXISTS `medication_logs` (
        `medication_id` INTEGER PRIMARY KEY AUTOINCREMENT,
        `timestamp` TEXT NOT NULL,
        `medication_name` TEXT NOT NULL,
        `scheduled_time` TEXT NOT NULL,
        `taken_time` TEXT,
        `status` TEXT NOT NULL,
        `compliance_score` INTEGER
    );"""
    ]
    
    # create a database connection
    conn = create_connection(database)

    # create tables
    if conn is not None:
        # create tables
        for table in tables:
            create_table(conn, table)
        conn.close()            
    else:
        ic2("Error! cannot create the database connection.")

def add_sensor_data(device_name, device_type, value, status='normal', location='home', alert_level='normal'):
    """
    Add new sensor data into the sensor_data table
    :param device_name: Name of the device
    :param device_type: Type of device (sensor, actuator, meter)
    :param value: Sensor reading value
    :param status: Device status
    :param location: Device location
    :param alert_level: Alert level (normal, warning, emergency)
    :return: last row id
    """
    sql = ''' INSERT INTO sensor_data(device_name, device_type, timestamp, value, status, location, alert_level)
              VALUES(?,?,?,?,?,?,?) '''
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute(sql, [device_name, device_type, timestamp(), value, status, location, alert_level])
        conn.commit()
        re = cur.lastrowid
        conn.close()
        return re
    else:
        ic2("Error! cannot create the database connection.")

def add_emergency_log(device_name, emergency_type, severity, message, response_time=None):
    """
    Add emergency log entry
    :param device_name: Name of the device that triggered emergency
    :param emergency_type: Type of emergency (fall, health, medication, etc.)
    :param severity: Severity level (low, medium, high, critical)
    :param message: Emergency message
    :param response_time: Response time in seconds
    :return: last row id
    """
    sql = ''' INSERT INTO emergency_logs(timestamp, device_name, emergency_type, severity, message, response_time)
              VALUES(?,?,?,?,?,?) '''
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute(sql, [timestamp(), device_name, emergency_type, severity, message, response_time])
        conn.commit()
        re = cur.lastrowid
        conn.close()
        return re
    else:
        ic2("Error! cannot create the database connection.")

def add_health_metrics(heart_rate, blood_pressure_systolic, blood_pressure_diastolic, temperature, oxygen_saturation):
    """
    Add health metrics data
    :param heart_rate: Heart rate in bpm
    :param blood_pressure_systolic: Systolic blood pressure
    :param blood_pressure_diastolic: Diastolic blood pressure
    :param temperature: Body temperature in Celsius
    :param oxygen_saturation: Oxygen saturation percentage
    :return: last row id
    """
    # Determine alert level based on thresholds
    alert_level = 'normal'
    if (heart_rate < HEART_RATE_MIN or heart_rate > HEART_RATE_MAX or
        blood_pressure_systolic > BLOOD_PRESSURE_SYSTOLIC_MAX or
        blood_pressure_diastolic > BLOOD_PRESSURE_DIASTOLIC_MAX or
        temperature < TEMPERATURE_MIN or temperature > TEMPERATURE_MAX or
        oxygen_saturation < 95):
        alert_level = 'warning'
    
    sql = ''' INSERT INTO health_metrics(timestamp, heart_rate, blood_pressure_systolic, blood_pressure_diastolic, temperature, oxygen_saturation, alert_level)
              VALUES(?,?,?,?,?,?,?) '''
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute(sql, [timestamp(), heart_rate, blood_pressure_systolic, blood_pressure_diastolic, temperature, oxygen_saturation, alert_level])
        conn.commit()
        re = cur.lastrowid
        conn.close()
        return re
    else:
        ic2("Error! cannot create the database connection.")

def add_medication_log(medication_name, scheduled_time, taken_time=None, status='scheduled', compliance_score=100):
    """
    Add medication log entry
    :param medication_name: Name of the medication
    :param scheduled_time: Scheduled time for medication
    :param taken_time: Actual time medication was taken
    :param status: Status (scheduled, taken, skipped, missed)
    :param compliance_score: Compliance score
    :return: last row id
    """
    sql = ''' INSERT INTO medication_logs(timestamp, medication_name, scheduled_time, taken_time, status, compliance_score)
              VALUES(?,?,?,?,?,?) '''
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute(sql, [timestamp(), medication_name, scheduled_time, taken_time, status, compliance_score])
        conn.commit()
        re = cur.lastrowid
        conn.close()
        return re
    else:
        ic2("Error! cannot create the database connection.")

def create_elderly_device(device_name, device_type, location, update_interval, pub_topic, sub_topic, emergency_contact=None, alert_threshold=None):
    """
    Create a new elderly care device entry
    :param device_name: Name of the device
    :param device_type: Type of device
    :param location: Device location
    :param update_interval: Update interval in seconds
    :param pub_topic: MQTT publish topic
    :param sub_topic: MQTT subscribe topic
    :param emergency_contact: Emergency contact information
    :param alert_threshold: Alert threshold values
    :return: device_id
    """
    sql = ''' INSERT INTO elderly_devices(device_name, device_type, status, location, last_updated, update_interval, enabled, alert_threshold, emergency_contact, pub_topic, sub_topic)
              VALUES(?,?,?,?,?,?,?,?,?,?,?) '''
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute(sql, [device_name, device_type, 'offline', location, timestamp(), update_interval, 1, alert_threshold, emergency_contact, pub_topic, sub_topic])
        conn.commit()
        re = cur.lastrowid
        conn.close()
        return re
    else:
        ic2("Error! cannot create the database connection.")

def timestamp():
    return str(datetime.fromtimestamp(datetime.timestamp(datetime.now()))).split('.')[0]

def fetch_sensor_data(device_name=None, device_type=None, hours=24):
    """
    Fetch sensor data from the database
    :param device_name: Filter by device name
    :param device_type: Filter by device type
    :param hours: Number of hours to fetch data for
    :return: DataFrame with sensor data
    """
    conn = create_connection()
    if conn is not None:
        query = "SELECT * FROM sensor_data WHERE timestamp >= datetime('now', '-{} hours')".format(hours)
        params = []
        
        if device_name:
            query += " AND device_name = ?"
            params.append(device_name)
        if device_type:
            query += " AND device_type = ?"
            params.append(device_type)
            
        query += " ORDER BY timestamp DESC"
        
        df = pd.read_sql_query(query, conn, params=params)
        conn.close()
        return df
    else:
        ic2("Error! cannot create the database connection.")
        return pd.DataFrame()

def fetch_emergency_logs(hours=24):
    """
    Fetch emergency logs from the database
    :param hours: Number of hours to fetch logs for
    :return: DataFrame with emergency logs
    """
    conn = create_connection()
    if conn is not None:
        query = "SELECT * FROM emergency_logs WHERE timestamp >= datetime('now', '-{} hours') ORDER BY timestamp DESC".format(hours)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    else:
        ic2("Error! cannot create the database connection.")
        return pd.DataFrame()

def fetch_health_metrics(hours=24):
    """
    Fetch health metrics from the database
    :param hours: Number of hours to fetch data for
    :return: DataFrame with health metrics
    """
    conn = create_connection()
    if conn is not None:
        query = "SELECT * FROM health_metrics WHERE timestamp >= datetime('now', '-{} hours') ORDER BY timestamp DESC".format(hours)
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df
    else:
        ic2("Error! cannot create the database connection.")
        return pd.DataFrame()

def get_device_status(device_name):
    """
    Get current status of a device
    :param device_name: Name of the device
    :return: Device status information
    """
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute("SELECT * FROM elderly_devices WHERE device_name = ?", (device_name,))
        row = cur.fetchone()
        conn.close()
        return row
    else:
        ic2("Error! cannot create the database connection.")
        return None

def update_device_status(device_name, status, last_updated=None):
    """
    Update device status
    :param device_name: Name of the device
    :param status: New status
    :param last_updated: Last updated timestamp
    :return: None
    """
    sql = ''' UPDATE elderly_devices SET status = ?, last_updated = ? WHERE device_name = ?'''
    conn = create_connection()
    if conn is not None:
        cur = conn.cursor()
        cur.execute(sql, [status, last_updated or timestamp(), device_name])
        conn.commit()
        conn.close()
    else:
        ic2("Error! cannot create the database connection.")

if __name__ == '__main__':
    if db_init:
        init_db(db_name)
        print("Database initialized successfully!")
        
        # Create sample devices
        create_elderly_device('FallDetector_001', 'sensor', 'Living Room', 1, 
                            comm_topic + 'sensors/fall_detection', 
                            comm_topic + 'sensors/fall_detection/control',
                            'Family: +1-555-0123', 'acceleration > 2.5g')
        
        create_elderly_device('HealthMonitor_001', 'sensor', 'Bedroom', 30, 
                            comm_topic + 'sensors/health_monitor', 
                            comm_topic + 'sensors/health_monitor/control',
                            'Doctor: +1-555-0456', 'HR < 50 or > 120')
        
        create_elderly_device('EmergencyButton_001', 'sensor', 'Multiple Locations', 0, 
                            comm_topic + 'sensors/emergency_button', 
                            comm_topic + 'sensors/emergency_button/control',
                            'Emergency: 911', 'button_pressed')
        
        create_elderly_device('SmartLighting_001', 'actuator', 'Whole House', 60, 
                            comm_topic + 'actuators/smart_lighting/status', 
                            comm_topic + 'actuators/smart_lighting/control',
                            'Family: +1-555-0123', 'motion_detected')
        
        create_elderly_device('MedicationReminder_001', 'meter', 'Kitchen', 3600, 
                            comm_topic + 'sensors/medication_reminder', 
                            comm_topic + 'sensors/medication_reminder/control',
                            'Family: +1-555-0123', 'medication_missed')
        
        print("Sample devices created successfully!")
    else:
        print("Database already initialized. Set db_init = True to reinitialize.")

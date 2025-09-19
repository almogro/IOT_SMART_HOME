# Elderly Care Smart Home Manager
# Collects data from MQTT broker and manages database operations

import paho.mqtt.client as mqtt
import time
import random
from init import *
import data_acq as da
from icecream import ic
from datetime import datetime 
import json

def time_format():
    return f'{datetime.now()}  Manager|> '

ic.configureOutput(prefix=time_format)
ic.configureOutput(includeContext=False)

# Define callback functions
def on_log(client, userdata, level, buf):
    ic("log: " + buf)
            
def on_connect(client, userdata, flags, rc):    
    if rc == 0:
        ic("connected OK")                
    else:
        ic("Bad connection Returned code=", rc)
        
def on_disconnect(client, userdata, flags, rc=0):    
    ic("DisConnected result code " + str(rc))
        
def on_message(client, userdata, msg):
    topic = msg.topic
    m_decode = str(msg.payload.decode("utf-8", "ignore"))
    ic("message from: " + topic, m_decode)
    process_message(topic, m_decode)

def send_msg(client, topic, message):
    ic("Sending message: " + message)
    client.publish(topic, message)   

def client_init(cname):
    r = random.randrange(1, 10000000)
    ID = str(cname + str(r + 21))
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, ID, clean_session=True)
    # define callback function       
    client.on_connect = on_connect
    client.on_disconnect = on_disconnect
    client.on_log = on_log
    client.on_message = on_message        
    if username != "":
        client.username_pw_set(username, password)        
    ic("Connecting to broker ", broker_ip)
    client.connect(broker_ip, int(port))
    return client

def process_message(topic, message):
    """Process incoming MQTT messages and store in database"""
    try:
        # Extract device information from topic
        device_name = extract_device_name(topic)
        device_type = extract_device_type(topic)
        
        # Determine alert level
        alert_level = 'normal'
        if 'EMERGENCY' in message.upper():
            alert_level = 'emergency'
        elif 'WARNING' in message.upper() or 'Warning' in message:
            alert_level = 'warning'
        
        # Store sensor data
        da.add_sensor_data(
            device_name=device_name,
            device_type=device_type,
            value=message,
            status='online',
            location=extract_location(topic),
            alert_level=alert_level
        )
        
        # Process specific message types
        if 'fall detected' in message.lower():
            process_fall_detection(message)
        elif 'health emergency' in message.lower():
            process_health_emergency(message)
        elif 'emergency button' in message.lower():
            process_emergency_button(message)
        elif 'medication' in message.lower():
            process_medication_event(message)
        elif 'light' in message.lower():
            process_lighting_event(message)
            
    except Exception as e:
        ic(f"Error processing message: {e}")

def extract_device_name(topic):
    """Extract device name from MQTT topic"""
    parts = topic.split('/')
    if len(parts) >= 3:
        return parts[2]  # Assuming topic format: elderly_care/sensors/device_name
    return 'unknown_device'

def extract_device_type(topic):
    """Extract device type from MQTT topic"""
    if 'sensors' in topic:
        return 'sensor'
    elif 'actuators' in topic:
        return 'actuator'
    elif 'meters' in topic:
        return 'meter'
    return 'unknown'

def extract_location(topic):
    """Extract location from MQTT topic or device name"""
    device_name = extract_device_name(topic)
    if 'fall' in device_name.lower():
        return 'Living Room'
    elif 'health' in device_name.lower():
        return 'Bedroom'
    elif 'emergency' in device_name.lower():
        return 'Multiple Locations'
    elif 'lighting' in device_name.lower():
        return 'Whole House'
    elif 'medication' in device_name.lower():
        return 'Kitchen'
    return 'Home'

def process_fall_detection(message):
    """Process fall detection emergency"""
    ic("FALL DETECTION EMERGENCY!")
    
    # Log emergency
    da.add_emergency_log(
        device_name='FallDetector',
        emergency_type='fall_detection',
        severity='critical',
        message=message,
        response_time=EMERGENCY_RESPONSE_TIME
    )
    
    # Send emergency notifications
    emergency_msg = f'EMERGENCY: Fall detected! {message}'
    send_msg(client, comm_topic + 'alerts/emergency', emergency_msg)
    send_msg(client, comm_topic + 'alerts/family', emergency_msg)
    
    # Activate emergency lighting
    send_msg(client, comm_topic + 'actuators/smart_lighting/control', 'EMERGENCY: Activate all lights')

def process_health_emergency(message):
    """Process health emergency"""
    ic("HEALTH EMERGENCY!")
    
    # Log emergency
    da.add_emergency_log(
        device_name='HealthMonitor',
        emergency_type='health_emergency',
        severity='high',
        message=message,
        response_time=EMERGENCY_RESPONSE_TIME
    )
    
    # Send emergency notifications
    emergency_msg = f'HEALTH EMERGENCY: {message}'
    send_msg(client, comm_topic + 'alerts/emergency', emergency_msg)
    send_msg(client, comm_topic + 'alerts/family', emergency_msg)
    send_msg(client, comm_topic + 'alerts/medical', emergency_msg)

def process_emergency_button(message):
    """Process emergency button press"""
    ic("EMERGENCY BUTTON PRESSED!")
    
    # Log emergency
    da.add_emergency_log(
        device_name='EmergencyButton',
        emergency_type='manual_emergency',
        severity='critical',
        message=message,
        response_time=0  # Immediate response
    )
    
    # Send emergency notifications
    emergency_msg = f'EMERGENCY BUTTON: {message}'
    send_msg(client, comm_topic + 'alerts/emergency', emergency_msg)
    send_msg(client, comm_topic + 'alerts/family', emergency_msg)
    send_msg(client, comm_topic + 'alerts/emergency_services', emergency_msg)
    
    # Activate emergency lighting
    send_msg(client, comm_topic + 'actuators/smart_lighting/control', 'EMERGENCY: Activate all lights')

def process_medication_event(message):
    """Process medication-related events"""
    if 'taken' in message.lower():
        ic("Medication taken")
        da.add_medication_log('Medication', datetime.now().strftime('%H:%M'), 
                            datetime.now().strftime('%H:%M'), 'taken', 100)
    elif 'skipped' in message.lower():
        ic("Medication skipped")
        da.add_medication_log('Medication', datetime.now().strftime('%H:%M'), 
                            None, 'skipped', 85)
    elif 'missed' in message.lower():
        ic("Medication missed - ALERT!")
        da.add_medication_log('Medication', datetime.now().strftime('%H:%M'), 
                            None, 'missed', 70)
        
        # Send medication alert
        alert_msg = f'MEDICATION ALERT: {message}'
        send_msg(client, comm_topic + 'alerts/medication', alert_msg)
        send_msg(client, comm_topic + 'alerts/family', alert_msg)

def process_lighting_event(message):
    """Process lighting control events"""
    ic(f"Lighting event: {message}")
    # Update device status
    da.update_device_status('SmartLighting_001', 'online')

def check_health_thresholds():
    """Check health data for threshold violations"""
    try:
        # Get recent health data
        health_data = da.fetch_health_metrics(hours=1)
        
        if not health_data.empty:
            latest = health_data.iloc[0]
            
            # Check for health warnings
            if latest['alert_level'] == 'warning':
                warning_msg = f'Health Warning: HR:{latest["heart_rate"]}, BP:{latest["blood_pressure_systolic"]}/{latest["blood_pressure_diastolic"]}, Temp:{latest["temperature"]}°C'
                send_msg(client, comm_topic + 'alerts/health_warning', warning_msg)
                
    except Exception as e:
        ic(f"Error checking health thresholds: {e}")

def check_medication_compliance():
    """Check medication compliance and send reminders"""
    try:
        # This would typically check scheduled medications
        # For now, we'll simulate a check
        current_hour = datetime.now().hour
        
        if current_hour in [8, 14, 20, 22]:  # Medication times
            reminder_msg = f'Medication Reminder: Time for scheduled medication at {current_hour}:00'
            send_msg(client, comm_topic + 'alerts/medication_reminder', reminder_msg)
            
    except Exception as e:
        ic(f"Error checking medication compliance: {e}")

def check_system_status():
    """Check overall system status and send periodic updates"""
    try:
        # Get device statuses
        devices = ['FallDetector_001', 'HealthMonitor_001', 'EmergencyButton_001', 
                  'SmartLighting_001', 'MedicationReminder_001']
        
        online_devices = 0
        for device in devices:
            status = da.get_device_status(device)
            if status and status[2] == 'online':  # status field
                online_devices += 1
        
        # Send system status
        status_msg = f'System Status: {online_devices}/{len(devices)} devices online'
        send_msg(client, comm_topic + 'system/status', status_msg)
        
    except Exception as e:
        ic(f"Error checking system status: {e}")

def main():    
    global client
    cname = "ElderlyCare-Manager-"
    client = client_init(cname)
    
    # main monitoring loop
    client.loop_start()
    client.subscribe(comm_topic + '#')
    
    try:
        while conn_time == 0:
            # Check various system conditions
            check_health_thresholds()
            check_medication_compliance()
            check_system_status()
            
            time.sleep(manag_time)
            
        ic("con_time ending") 
    except KeyboardInterrupt:
        client.disconnect()
        ic("interrupted by keyboard")

    client.loop_stop()
    client.disconnect()
    ic("End manager run script")

if __name__ == "__main__":
    main()

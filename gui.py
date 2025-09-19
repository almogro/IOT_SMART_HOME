# Elderly Care Smart Home Main GUI Application
import os
import sys
import random
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from matplotlib.pyplot import get
BASE_PATH = os.path.abspath(os.path.dirname(__file__))
from init import *
from agent import Mqtt_client 
import time
from icecream import ic
from datetime import datetime 
import data_acq as da
import pyqtgraph as pg
import logging

# Gets or creates a logger
logger = logging.getLogger(__name__)  

# set log level
logger.setLevel(logging.WARNING)

# define file handler and set formatter
file_handler = logging.FileHandler('logfile_gui.log')
formatter = logging.Formatter('%(asctime)s : %(levelname)s : %(name)s : %(message)s')
file_handler.setFormatter(formatter)

# add file handler to logger
logger.addHandler(file_handler)

def time_format():
    return f'{datetime.now()}  GUI|> '

ic.configureOutput(prefix=time_format)
ic.configureOutput(includeContext=False)

# Creating Client name - should be unique 
global clientname
r = random.randrange(1, 10000)
clientname = "ElderlyCare_GUI_" + str(r)

def check(fnk):    
    try:
        rz = fnk
    except:
        rz = 'NA'
    return rz        

class MC(Mqtt_client):
    def __init__(self):
        super().__init__()
        
    def on_message(self, client, userdata, msg):
        topic = msg.topic            
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        ic("message from:" + topic, m_decode)
        
        # Process different types of messages
        if 'fall_detection' in topic:
            mainwin.emergencyDock.update_fall_status(m_decode)
        elif 'health_monitor' in topic:
            mainwin.healthDock.update_health_data(m_decode)
        elif 'emergency_button' in topic:
            mainwin.emergencyDock.update_emergency_status(m_decode)
        elif 'smart_lighting' in topic:
            mainwin.controlDock.update_lighting_status(m_decode)
        elif 'medication_reminder' in topic:
            mainwin.medicationDock.update_medication_status(m_decode)
        elif 'alerts' in topic:
            mainwin.alertsDock.update_alerts(m_decode)

class ConnectionDock(QDockWidget):
    """Connection Management Dock"""
    def __init__(self, mc):
        QDockWidget.__init__(self)        
        self.mc = mc
        self.topic = comm_topic + '#'        
        self.mc.set_on_connected_to_form(self.on_connected)        
        
        self.eHostInput = QLineEdit()
        self.eHostInput.setInputMask('999.999.999.999')
        self.eHostInput.setText(broker_ip)        
        
        self.ePort = QLineEdit()
        self.ePort.setValidator(QIntValidator())
        self.ePort.setMaxLength(4)
        self.ePort.setText(broker_port)        
        
        self.eClientID = QLineEdit()
        global clientname
        self.eClientID.setText(clientname)        
        
        self.eConnectButton = QPushButton("Connect", self)
        self.eConnectButton.setToolTip("click me to connect")
        self.eConnectButton.clicked.connect(self.on_button_connect_click)
        self.eConnectButton.setStyleSheet("background-color: red")        
        
        formLayot = QFormLayout()
        formLayot.addRow("Host", self.eHostInput)
        formLayot.addRow("Port", self.ePort)        
        formLayot.addRow("", self.eConnectButton)
        
        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("Connection") 
        
    def on_connected(self):
        self.eConnectButton.setStyleSheet("background-color: green")
        self.eConnectButton.setText('Connected')
            
    def on_button_connect_click(self):
        self.mc.set_broker(self.eHostInput.text())
        self.mc.set_port(int(self.ePort.text()))
        self.mc.set_clientName(self.eClientID.text())           
        self.mc.connect_to()        
        self.mc.start_listening()
        time.sleep(1)
        if not self.mc.subscribed:
            self.mc.subscribe_to(self.topic)

class EmergencyDock(QDockWidget):
    """Emergency Status and Fall Detection Dock"""
    def __init__(self, mc):
        QDockWidget.__init__(self)        
        self.mc = mc
        
        # Emergency status indicators
        self.emergencyStatus = QLabel()
        self.emergencyStatus.setText("System Normal")
        self.emergencyStatus.setStyleSheet("color: green; font-size: 16px; font-weight: bold")
        
        self.fallStatus = QLabel()
        self.fallStatus.setText("No Fall Detected")
        self.fallStatus.setStyleSheet("color: green")
        
        self.emergencyButtonStatus = QLabel()
        self.emergencyButtonStatus.setText("Emergency Button Ready")
        self.emergencyButtonStatus.setStyleSheet("color: green")
        
        self.lastEmergency = QTextEdit()
        self.lastEmergency.setMaximumHeight(100)
        self.lastEmergency.setReadOnly(True)
        
        self.emergencyCount = QLabel()
        self.emergencyCount.setText("Emergencies Today: 0")
        
        formLayot = QFormLayout()
        formLayot.addRow("Emergency Status", self.emergencyStatus)
        formLayot.addRow("Fall Detection", self.fallStatus)
        formLayot.addRow("Emergency Button", self.emergencyButtonStatus)
        formLayot.addRow("Last Emergency", self.lastEmergency)
        formLayot.addRow("Emergency Count", self.emergencyCount)
        
        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("Emergency Status") 
        
    def update_fall_status(self, message):
        if 'FALL DETECTED' in message.upper():
            self.fallStatus.setText("FALL DETECTED!")
            self.fallStatus.setStyleSheet("color: red; font-weight: bold")
            self.emergencyStatus.setText("EMERGENCY!")
            self.emergencyStatus.setStyleSheet("color: red; font-size: 16px; font-weight: bold")
            self.lastEmergency.append(f"{datetime.now().strftime('%H:%M:%S')}: {message}")
            
            # Update emergency count for fall detection
            current_count = int(self.emergencyCount.text().split(": ")[1])
            self.emergencyCount.setText(f"Emergencies Today: {current_count + 1}")
            self.emergencyCount.setStyleSheet("color: red; font-weight: bold")
            
            # Set a timer to reset fall status after 10 seconds
            QTimer.singleShot(10000, self.reset_fall_status)
        # Don't reset immediately on "Normal" messages - let the timer handle it
    
    def reset_fall_status(self):
        """Reset fall status after a delay"""
        self.fallStatus.setText("No Fall Detected")
        self.fallStatus.setStyleSheet("color: green")
            
    def update_emergency_status(self, message):
        # Check for emergency but ignore reset messages
        if 'EMERGENCY' in message.upper() and 'RESET' not in message.upper():
            self.emergencyButtonStatus.setText("EMERGENCY TRIGGERED!")
            self.emergencyButtonStatus.setStyleSheet("color: red; font-weight: bold")
            self.emergencyStatus.setText("EMERGENCY!")
            self.emergencyStatus.setStyleSheet("color: red; font-size: 16px; font-weight: bold")
            self.lastEmergency.append(f"{datetime.now().strftime('%H:%M:%S')}: {message}")
            
            # Update emergency count
            current_count = int(self.emergencyCount.text().split(": ")[1])
            self.emergencyCount.setText(f"Emergencies Today: {current_count + 1}")
            self.emergencyCount.setStyleSheet("color: red; font-weight: bold")
        elif 'RESET' in message.upper():
            # Handle reset message - reset button status to ready
            self.emergencyButtonStatus.setText("Emergency Button Ready")
            self.emergencyButtonStatus.setStyleSheet("color: green")

class HealthDock(QDockWidget):
    """Health Monitoring Dock"""
    def __init__(self, mc):
        QDockWidget.__init__(self)        
        self.mc = mc
        
        # Health metrics display
        self.heartRate = QLabel()
        self.heartRate.setText("Heart Rate: -- bpm")
        
        self.bloodPressure = QLabel()
        self.bloodPressure.setText("Blood Pressure: --/--")
        
        self.temperature = QLabel()
        self.temperature.setText("Temperature: --°C")
        
        self.oxygenSaturation = QLabel()
        self.oxygenSaturation.setText("Oxygen Saturation: --%")
        
        self.healthStatus = QLabel()
        self.healthStatus.setText("Health Status: Normal")
        self.healthStatus.setStyleSheet("color: green")
        
        self.healthAlerts = QTextEdit()
        self.healthAlerts.setMaximumHeight(100)
        self.healthAlerts.setReadOnly(True)
        
        formLayot = QFormLayout()
        formLayot.addRow("Heart Rate", self.heartRate)
        formLayot.addRow("Blood Pressure", self.bloodPressure)
        formLayot.addRow("Temperature", self.temperature)
        formLayot.addRow("Oxygen Saturation", self.oxygenSaturation)
        formLayot.addRow("Health Status", self.healthStatus)
        formLayot.addRow("Health Alerts", self.healthAlerts)
        
        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("Health Monitoring") 
        
    def update_health_data(self, message):
        try:
            if 'HR:' in message:
                hr = message.split('HR:')[1].split(',')[0].strip()
                self.heartRate.setText(f"Heart Rate: {hr} bpm")
                
                # Check for abnormal heart rate
                if hr.isdigit():
                    hr_val = int(hr)
                    if hr_val < HEART_RATE_MIN or hr_val > HEART_RATE_MAX:
                        self.healthStatus.setText("Health Status: WARNING")
                        self.healthStatus.setStyleSheet("color: orange")
                        self.healthAlerts.append(f"{datetime.now().strftime('%H:%M:%S')}: Abnormal heart rate: {hr} bpm")
            
            if 'BP:' in message:
                bp = message.split('BP:')[1].split(',')[0].strip()
                self.bloodPressure.setText(f"Blood Pressure: {bp}")
            
            if 'Temp:' in message:
                temp = message.split('Temp:')[1].split('°C')[0].strip()
                self.temperature.setText(f"Temperature: {temp}°C")
                
                # Check for abnormal temperature
                if temp.replace('.', '').isdigit():
                    temp_val = float(temp)
                    if temp_val < TEMPERATURE_MIN or temp_val > TEMPERATURE_MAX:
                        self.healthStatus.setText("Health Status: WARNING")
                        self.healthStatus.setStyleSheet("color: orange")
                        self.healthAlerts.append(f"{datetime.now().strftime('%H:%M:%S')}: Abnormal temperature: {temp}°C")
            
            if 'O2:' in message:
                o2 = message.split('O2:')[1].split('%')[0].strip()
                self.oxygenSaturation.setText(f"Oxygen Saturation: {o2}%")
                
        except Exception as e:
            ic(f"Error parsing health data: {e}")

class ControlDock(QDockWidget):
    """Smart Home Control Dock"""
    def __init__(self, mc):
        QDockWidget.__init__(self)        
        self.mc = mc
        
        # Lighting controls
        self.livingRoomLight = QPushButton("Living Room Light")
        self.livingRoomLight.clicked.connect(lambda: self.toggle_light("Living Room"))
        self.livingRoomLight.setStyleSheet("background-color: gray")
        
        self.bedroomLight = QPushButton("Bedroom Light")
        self.bedroomLight.clicked.connect(lambda: self.toggle_light("Bedroom"))
        self.bedroomLight.setStyleSheet("background-color: gray")
        
        self.bathroomLight = QPushButton("Bathroom Light")
        self.bathroomLight.clicked.connect(lambda: self.toggle_light("Bathroom"))
        self.bathroomLight.setStyleSheet("background-color: gray")
        
        self.kitchenLight = QPushButton("Kitchen Light")
        self.kitchenLight.clicked.connect(lambda: self.toggle_light("Kitchen"))
        self.kitchenLight.setStyleSheet("background-color: gray")
        
        # Emergency controls
        self.emergencyLighting = QPushButton("🚨 EMERGENCY LIGHTING 🚨")
        self.emergencyLighting.clicked.connect(self.activate_emergency_lighting)
        self.emergencyLighting.setStyleSheet("background-color: red; font-weight: bold")
        
        # Reset button
        self.resetLights = QPushButton("Reset All Lights")
        self.resetLights.clicked.connect(self.reset_all_lights)
        self.resetLights.setStyleSheet("background-color: orange; font-weight: bold")
        
        # Status display
        self.lightingStatus = QTextEdit()
        self.lightingStatus.setMaximumHeight(100)
        self.lightingStatus.setReadOnly(True)
        self.lightingStatus.setText("All lights OFF")
        
        # Track button states
        self.light_states = {
            'Living Room': False,
            'Bedroom': False,
            'Bathroom': False,
            'Kitchen': False
        }
        
        formLayot = QFormLayout()
        formLayot.addRow("Living Room", self.livingRoomLight)
        formLayot.addRow("Bedroom", self.bedroomLight)
        formLayot.addRow("Bathroom", self.bathroomLight)
        formLayot.addRow("Kitchen", self.kitchenLight)
        formLayot.addRow("", self.emergencyLighting)
        formLayot.addRow("", self.resetLights)
        formLayot.addRow("Status", self.lightingStatus)
        
        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("Smart Controls") 
        
    def toggle_light(self, room):
        # Toggle light state
        # Convert "Living Room" to "livingRoomLight" format
        room_attr = room.replace(" ", "")
        room_attr = room_attr[0].lower() + room_attr[1:] + "Light"
        button = getattr(self, room_attr)
        
        # Toggle the state
        self.light_states[room] = not self.light_states[room]
        
        if self.light_states[room]:
            button.setStyleSheet("background-color: yellow")
            status = "ON"
        else:
            button.setStyleSheet("background-color: gray")
            status = "OFF"
            
        # Send MQTT command
        self.mc.publish_to(comm_topic + 'actuators/smart_lighting/control', f'Turn {status} {room} light')
        
        # Update status display
        self.update_lighting_status(f"{room} light turned {status}")
        
    def activate_emergency_lighting(self):
        try:
            ic("Starting emergency lighting activation...")
            
            # Turn on all lights and update states
            lights = [self.livingRoomLight, self.bedroomLight, self.bathroomLight, self.kitchenLight]
            light_names = ['Living Room', 'Bedroom', 'Bathroom', 'Kitchen']
            
            ic(f"Found {len(lights)} lights to activate")
            
            for i, (light, name) in enumerate(zip(lights, light_names)):
                try:
                    ic(f"Activating light {i+1}: {name}")
                    light.setStyleSheet("background-color: red")
                    self.light_states[name] = True
                    ic(f"Light {name} activated successfully")
                except Exception as light_error:
                    ic(f"Error activating light {name}: {light_error}")
                    continue
                
            ic("All lights activated, sending MQTT message...")
            
            # Send MQTT message
            try:
                topic = comm_topic + 'actuators/smart_lighting/control'
                message = 'EMERGENCY: Activate all lights'
                ic(f"Publishing to topic: {topic}")
                ic(f"Message: {message}")
                
                if hasattr(self.mc, 'publish_to') and callable(getattr(self.mc, 'publish_to')):
                    self.mc.publish_to(topic, message)
                    ic("MQTT message sent successfully")
                else:
                    ic("ERROR: publish_to method not available")
                    
            except Exception as mqtt_error:
                ic(f"MQTT publish error: {mqtt_error}")
                
            ic("Updating lighting status...")
            self.update_lighting_status("EMERGENCY: All lights activated")
            ic("Emergency lighting activation completed")
            
        except Exception as e:
            ic(f"Critical error in emergency lighting: {e}")
            ic(f"Error type: {type(e)}")
            try:
                self.update_lighting_status(f"ERROR: Emergency lighting failed - {e}")
            except:
                ic("Could not update lighting status due to error")
        
    def reset_all_lights(self):
        """Reset all lights to OFF state"""
        try:
            lights = [self.livingRoomLight, self.bedroomLight, self.bathroomLight, self.kitchenLight]
            light_names = ['Living Room', 'Bedroom', 'Bathroom', 'Kitchen']
            
            for light, name in zip(lights, light_names):
                light.setStyleSheet("background-color: gray")
                self.light_states[name] = False
                
            self.mc.publish_to(comm_topic + 'actuators/smart_lighting/control', 'Reset: All lights turned OFF')
            self.update_lighting_status("Reset: All lights turned OFF")
        except Exception as e:
            ic(f"Error resetting lights: {e}")
            self.update_lighting_status(f"ERROR: Reset failed - {e}")
    
    def update_lighting_status(self, message):
        try:
            ic(f"Updating lighting status with message: {message}")
            if hasattr(self, 'lightingStatus') and self.lightingStatus is not None:
                timestamp = datetime.now().strftime('%H:%M:%S')
                status_text = f"{timestamp}: {message}"
                self.lightingStatus.append(status_text)
                ic(f"Status updated successfully: {status_text}")
            else:
                ic("ERROR: lightingStatus widget not available")
        except Exception as e:
            ic(f"Error updating lighting status: {e}")
            ic(f"Error type: {type(e)}")
            # Try to print the error to console as fallback
            print(f"Lighting status update failed: {e}")

class MedicationDock(QDockWidget):
    """Medication Management Dock"""
    def __init__(self, mc):
        QDockWidget.__init__(self)        
        self.mc = mc
        
        # Medication schedule
        self.medicationSchedule = QListWidget()
        self.medicationSchedule.addItem("8:00 AM - Blood Pressure Medication")
        self.medicationSchedule.addItem("2:00 PM - Heart Medicine")
        self.medicationSchedule.addItem("8:00 PM - Vitamins")
        self.medicationSchedule.addItem("10:00 PM - Sleep Aid")
        
        # Medication status
        self.medicationStatus = QLabel()
        self.medicationStatus.setText("Next: Blood Pressure at 8:00 AM")
        self.medicationStatus.setStyleSheet("color: green")
        
        # Compliance meter
        self.complianceMeter = QProgressBar()
        self.complianceMeter.setValue(85)
        self.complianceMeter.setMaximum(100)
        
        self.complianceLabel = QLabel("Compliance: 85%")
        
        # Control buttons
        self.takeMedication = QPushButton("✅ Take Medication")
        self.takeMedication.clicked.connect(self.take_medication)
        self.takeMedication.setStyleSheet("background-color: green")
        
        self.skipMedication = QPushButton("⏭️ Skip Medication")
        self.skipMedication.clicked.connect(self.skip_medication)
        self.skipMedication.setStyleSheet("background-color: orange")
        
        # Medication alerts
        self.medicationAlerts = QTextEdit()
        self.medicationAlerts.setMaximumHeight(100)
        self.medicationAlerts.setReadOnly(True)
        
        formLayot = QFormLayout()
        formLayot.addRow("Schedule", self.medicationSchedule)
        formLayot.addRow("Status", self.medicationStatus)
        formLayot.addRow("Compliance", self.complianceMeter)
        formLayot.addRow("", self.complianceLabel)
        formLayot.addRow("", self.takeMedication)
        formLayot.addRow("", self.skipMedication)
        formLayot.addRow("Alerts", self.medicationAlerts)
        
        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("Medication Management") 
        
    def take_medication(self):
        self.mc.publish_to(comm_topic + 'sensors/medication_reminder', 'Medication Taken')
        self.medicationAlerts.append(f"{datetime.now().strftime('%H:%M:%S')}: Medication taken")
        
    def skip_medication(self):
        self.mc.publish_to(comm_topic + 'sensors/medication_reminder', 'Medication Skipped')
        self.medicationAlerts.append(f"{datetime.now().strftime('%H:%M:%S')}: Medication skipped")
        
    def update_medication_status(self, message):
        if 'taken' in message.lower():
            self.medicationAlerts.append(f"{datetime.now().strftime('%H:%M:%S')}: {message}")
        elif 'skipped' in message.lower():
            self.medicationAlerts.append(f"{datetime.now().strftime('%H:%M:%S')}: {message}")
        elif 'missed' in message.lower():
            self.medicationStatus.setText("MISSED MEDICATION ALERT!")
            self.medicationStatus.setStyleSheet("color: red")
            self.medicationAlerts.append(f"{datetime.now().strftime('%H:%M:%S')}: {message}")

class AlertsDock(QDockWidget):
    """System Alerts and Notifications Dock"""
    def __init__(self, mc):
        QDockWidget.__init__(self)        
        self.mc = mc
        
        # Alerts display
        self.alertsDisplay = QTextEdit()
        self.alertsDisplay.setReadOnly(True)
        
        # Alert counters
        self.emergencyCount = QLabel()
        self.emergencyCount.setText("Emergencies: 0")
        
        self.warningCount = QLabel()
        self.warningCount.setText("Warnings: 0")
        
        self.infoCount = QLabel()
        self.infoCount.setText("Info: 0")
        
        # Clear button
        self.clearAlerts = QPushButton("Clear Alerts")
        self.clearAlerts.clicked.connect(self.clear_alerts)
        self.clearAlerts.setStyleSheet("background-color: orange")
        
        formLayot = QFormLayout()
        formLayot.addRow("Alerts", self.alertsDisplay)
        formLayot.addRow("Emergency Count", self.emergencyCount)
        formLayot.addRow("Warning Count", self.warningCount)
        formLayot.addRow("Info Count", self.infoCount)
        formLayot.addRow("", self.clearAlerts)
        
        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("System Alerts") 
        
        # Initialize counters
        self.emergency_count = 0
        self.warning_count = 0
        self.info_count = 0
        
    def update_alerts(self, message):
        timestamp = datetime.now().strftime('%H:%M:%S')
        self.alertsDisplay.append(f"[{timestamp}] {message}")
        
        # Update counters based on message type
        if 'EMERGENCY' in message.upper():
            self.emergency_count += 1
            self.emergencyCount.setText(f"Emergencies: {self.emergency_count}")
            self.emergencyCount.setStyleSheet("color: red; font-weight: bold")
        elif 'WARNING' in message.upper() or 'Warning' in message:
            self.warning_count += 1
            self.warningCount.setText(f"Warnings: {self.warning_count}")
            self.warningCount.setStyleSheet("color: orange")
        else:
            self.info_count += 1
            self.infoCount.setText(f"Info: {self.info_count}")
            
    def clear_alerts(self):
        self.alertsDisplay.clear()
        self.emergency_count = 0
        self.warning_count = 0
        self.info_count = 0
        self.emergencyCount.setText("Emergencies: 0")
        self.warningCount.setText("Warnings: 0")
        self.infoCount.setText("Info: 0")
        self.emergencyCount.setStyleSheet("color: black")
        self.warningCount.setStyleSheet("color: black")
        
        # Also reset emergency count in EmergencyDock
        mainwin.emergencyDock.emergencyCount.setText("Emergencies Today: 0")
        mainwin.emergencyDock.emergencyCount.setStyleSheet("color: black")
        mainwin.emergencyDock.emergencyStatus.setText("System Normal")
        mainwin.emergencyDock.emergencyStatus.setStyleSheet("color: green; font-size: 16px; font-weight: bold")
        mainwin.emergencyDock.fallStatus.setText("No Fall Detected")
        mainwin.emergencyDock.fallStatus.setStyleSheet("color: green")
        mainwin.emergencyDock.emergencyButtonStatus.setText("Emergency Button Ready")
        mainwin.emergencyDock.emergencyButtonStatus.setStyleSheet("color: green")

class MainWindow(QMainWindow):    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)                
        # Init of Mqtt_client class
        self.mc = MC()        
        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)
        # set up main window
        self.setGeometry(30, 100, 1200, 800)
        self.setWindowTitle('Elderly Care Smart Home System')
        
        # Init QDockWidget objects        
        self.connectionDock = ConnectionDock(self.mc)        
        self.emergencyDock = EmergencyDock(self.mc)
        self.healthDock = HealthDock(self.mc)
        self.controlDock = ControlDock(self.mc)
        self.medicationDock = MedicationDock(self.mc)
        self.alertsDock = AlertsDock(self.mc)
        
        # Add dock widgets
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.emergencyDock)
        self.addDockWidget(Qt.LeftDockWidgetArea, self.healthDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.controlDock)
        self.addDockWidget(Qt.RightDockWidgetArea, self.medicationDock)
        self.addDockWidget(Qt.BottomDockWidgetArea, self.alertsDock)
        
        # Make all dock widgets non-resizable and non-movable
        for dock in [self.connectionDock, self.emergencyDock, self.healthDock, 
                    self.controlDock, self.medicationDock, self.alertsDock]:
            dock.setFeatures(QDockWidget.NoDockWidgetFeatures)

if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        mainwin = MainWindow()
        mainwin.show()
        app.exec_()
    except:
        logger.exception("GUI Crash!")

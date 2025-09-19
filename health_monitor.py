# Health Monitor Emulator for Elderly Care Smart Home
import os
import sys
import PyQt5
import random
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import paho.mqtt.client as mqtt
import time
import datetime
from init import *
from agent import Mqtt_client
from icecream import ic

# Creating Client name - should be unique 
global clientname, CONNECTED
CONNECTED = False
r = random.randrange(1, 10000000)
clientname = "HealthMonitor_" + str(r)
health_topic = comm_topic + 'sensors/health_monitor'

class MC(Mqtt_client):
    def __init__(self):
        super().__init__()
        
    def on_message(self, client, userdata, msg):
        topic = msg.topic
        m_decode = str(msg.payload.decode("utf-8", "ignore"))
        ic("message from:" + topic, m_decode)
        try:
            mainwin.connectionDock.update_btn_state(m_decode)
        except:
            ic("fail in update button state")

class ConnectionDock(QDockWidget):
    """Health Monitor Connection Dock"""
    def __init__(self, mc):
        QDockWidget.__init__(self)        
        self.mc = mc
        self.mc.set_on_connected_to_form(self.on_connected)
        
        # Connection settings
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
        
        self.eUserName = QLineEdit()
        self.eUserName.setText(username)        
        
        self.ePassword = QLineEdit()
        self.ePassword.setEchoMode(QLineEdit.Password)
        self.ePassword.setText(password)        
        
        self.eConnectbtn = QPushButton("Enable/Connect", self)
        self.eConnectbtn.setToolTip("click me to connect")
        self.eConnectbtn.clicked.connect(self.on_button_connect_click)
        self.eConnectbtn.setStyleSheet("background-color: gray")
        
        # Health data display
        self.ePublisherTopic = QLineEdit()
        self.ePublisherTopic.setText(health_topic)
        
        self.heartRate = QLineEdit()
        self.heartRate.setText('72')
        
        self.bloodPressureSystolic = QLineEdit()
        self.bloodPressureSystolic.setText('120')
        
        self.bloodPressureDiastolic = QLineEdit()
        self.bloodPressureDiastolic.setText('80')
        
        self.temperature = QLineEdit()
        self.temperature.setText('36.5')
        
        self.oxygenSaturation = QLineEdit()
        self.oxygenSaturation.setText('98')
        
        self.healthStatus = QLineEdit()
        self.healthStatus.setText('Normal')
        self.healthStatus.setStyleSheet("color: green")
        
        self.emergencyButton = QPushButton("SIMULATE HEALTH EMERGENCY", self)
        self.emergencyButton.setToolTip("Simulate health emergency")
        self.emergencyButton.clicked.connect(self.simulate_emergency)
        self.emergencyButton.setStyleSheet("background-color: red")
        
        self.resetButton = QPushButton("Reset Status", self)
        self.resetButton.setToolTip("Reset health monitoring status")
        self.resetButton.clicked.connect(self.reset_status)
        self.resetButton.setStyleSheet("background-color: orange")
        
        formLayot = QFormLayout()
        formLayot.addRow("Turn On/Off", self.eConnectbtn)
        formLayot.addRow("Pub topic", self.ePublisherTopic)
        formLayot.addRow("Heart Rate (bpm)", self.heartRate)
        formLayot.addRow("BP Systolic", self.bloodPressureSystolic)
        formLayot.addRow("BP Diastolic", self.bloodPressureDiastolic)
        formLayot.addRow("Temperature (°C)", self.temperature)
        formLayot.addRow("Oxygen Saturation (%)", self.oxygenSaturation)
        formLayot.addRow("Health Status", self.healthStatus)
        formLayot.addRow("", self.emergencyButton)
        formLayot.addRow("", self.resetButton)
        
        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("Health Monitor") 
        
    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")
                    
    def on_button_connect_click(self):
        self.mc.set_broker(self.eHostInput.text())
        self.mc.set_port(int(self.ePort.text()))
        self.mc.set_clientName(self.eClientID.text())
        self.mc.set_username(self.eUserName.text())
        self.mc.set_password(self.ePassword.text())        
        self.mc.connect_to()        
        self.mc.start_listening()
        
    def update_btn_state(self, messg):
        if 'Emergency' in messg:
            self.healthStatus.setText('HEALTH EMERGENCY')
            self.healthStatus.setStyleSheet("color: red")
        elif 'Warning' in messg:
            self.healthStatus.setText('Warning')
            self.healthStatus.setStyleSheet("color: orange")
        elif 'Normal' in messg:
            self.healthStatus.setText('Normal')
            self.healthStatus.setStyleSheet("color: green")
            
    def simulate_emergency(self):
        # Simulate health emergency with dangerous values
        heart_rate = random.randint(150, 180)
        bp_systolic = random.randint(200, 220)
        bp_diastolic = random.randint(120, 140)
        temperature = random.uniform(39.5, 41.0)
        oxygen_sat = random.randint(85, 90)
        
        self.heartRate.setText(str(heart_rate))
        self.bloodPressureSystolic.setText(str(bp_systolic))
        self.bloodPressureDiastolic.setText(str(bp_diastolic))
        self.temperature.setText(f"{temperature:.1f}")
        self.oxygenSaturation.setText(str(oxygen_sat))
        
        self.healthStatus.setText('HEALTH EMERGENCY!')
        self.healthStatus.setStyleSheet("color: red")
        
        current_data = f'EMERGENCY: Health emergency detected! HR:{heart_rate}, BP:{bp_systolic}/{bp_diastolic}, Temp:{temperature:.1f}°C, O2:{oxygen_sat}%'
        self.mc.publish_to(self.ePublisherTopic.text(), current_data)
    
    def reset_status(self):
        """Reset health monitoring status to normal"""
        try:
            # Reset to normal values
            self.heartRate.setText("72")
            self.bloodPressureSystolic.setText("120")
            self.bloodPressureDiastolic.setText("80")
            self.temperature.setText("36.5")
            self.oxygenSaturation.setText("98")
            
            self.healthStatus.setText('Normal')
            self.healthStatus.setStyleSheet("color: green")
            
            current_data = 'Reset: Health monitoring status reset to normal'
            self.mc.publish_to(self.ePublisherTopic.text(), current_data)
            ic("Health monitoring status reset to normal")
        except Exception as e:
            ic(f"Error resetting health status: {e}")
            print(f"Error resetting health status: {e}")

class MainWindow(QMainWindow):    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)        
        # Init of Mqtt_client class        
        self.mc = MC()
        
        # Creating timer for continuous monitoring
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_health_data)
        self.timer.start(5000)  # Update every 5 seconds
        
        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)
        # set up main window
        self.setGeometry(30, 400, 400, 300)
        self.setWindowTitle('Health Monitor')
        # Init QDockWidget objects        
        self.connectionDock = ConnectionDock(self.mc)       
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)        

    def update_health_data(self):
        if not self.mc.connected:
            return
            
        # Simulate normal health data with small variations
        heart_rate = random.randint(65, 85)
        bp_systolic = random.randint(110, 130)
        bp_diastolic = random.randint(70, 85)
        temperature = random.uniform(36.0, 37.2)
        oxygen_sat = random.randint(95, 100)
        
        self.connectionDock.heartRate.setText(str(heart_rate))
        self.connectionDock.bloodPressureSystolic.setText(str(bp_systolic))
        self.connectionDock.bloodPressureDiastolic.setText(str(bp_diastolic))
        self.connectionDock.temperature.setText(f"{temperature:.1f}")
        self.connectionDock.oxygenSaturation.setText(str(oxygen_sat))
        
        # Check for health warnings
        status = "Normal"
        status_color = "color: green"
        
        if heart_rate < HEART_RATE_MIN or heart_rate > HEART_RATE_MAX:
            status = "Warning"
            status_color = "color: orange"
        if bp_systolic > BLOOD_PRESSURE_SYSTOLIC_MAX or bp_diastolic > BLOOD_PRESSURE_DIASTOLIC_MAX:
            status = "Warning"
            status_color = "color: orange"
        if temperature < TEMPERATURE_MIN or temperature > TEMPERATURE_MAX:
            status = "Warning"
            status_color = "color: orange"
        if oxygen_sat < 95:
            status = "Warning"
            status_color = "color: orange"
            
        self.connectionDock.healthStatus.setText(status)
        self.connectionDock.healthStatus.setStyleSheet(status_color)
        
        current_data = f'Normal: HR:{heart_rate}, BP:{bp_systolic}/{bp_diastolic}, Temp:{temperature:.1f}°C, O2:{oxygen_sat}%'
        self.mc.publish_to(health_topic, current_data)

if __name__ == '__main__':
    try:    
        app = QApplication(sys.argv)
        mainwin = MainWindow()
        mainwin.show()
        app.exec_()
    except Exception as e:
        print(f"Error: {e}")

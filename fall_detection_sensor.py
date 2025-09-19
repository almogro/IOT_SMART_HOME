# Fall Detection Sensor Emulator for Elderly Care Smart Home
import os
import sys
import PyQt5
import random
import math
from PyQt5 import QtGui, QtCore, QtWidgets
from PyQt5.QtWidgets import *
from PyQt5.QtGui import *
from PyQt5.QtCore import *
import paho.mqtt.client as mqtt
import time
import datetime
from init import *
from agent import Mqtt_client

# Creating Client name - should be unique 
global clientname, CONNECTED
CONNECTED = False
r = random.randrange(1, 10000000)
clientname = "FallDetector_" + str(r)
fall_topic = comm_topic + 'sensors/fall_detection'

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
    """Fall Detection Sensor Connection Dock"""
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
        
        # Sensor data display
        self.ePublisherTopic = QLineEdit()
        self.ePublisherTopic.setText(fall_topic)
        
        self.accelerationX = QLineEdit()
        self.accelerationX.setText('0.0')
        self.accelerationY = QLineEdit()
        self.accelerationY.setText('0.0')
        self.accelerationZ = QLineEdit()
        self.accelerationZ.setText('9.8')
        
        self.fallStatus = QLineEdit()
        self.fallStatus.setText('Normal')
        self.fallStatus.setStyleSheet("color: green")
        
        self.emergencyButton = QPushButton("EMERGENCY FALL DETECTED", self)
        self.emergencyButton.setToolTip("Simulate fall detection")
        self.emergencyButton.clicked.connect(self.simulate_fall)
        self.emergencyButton.setStyleSheet("background-color: red")
        
        self.resetButton = QPushButton("Reset Status", self)
        self.resetButton.setToolTip("Reset fall detection status")
        self.resetButton.clicked.connect(self.reset_status)
        self.resetButton.setStyleSheet("background-color: orange")
        
        formLayot = QFormLayout()
        formLayot.addRow("Turn On/Off", self.eConnectbtn)
        formLayot.addRow("Pub topic", self.ePublisherTopic)
        formLayot.addRow("Acceleration X", self.accelerationX)
        formLayot.addRow("Acceleration Y", self.accelerationY)
        formLayot.addRow("Acceleration Z", self.accelerationZ)
        formLayot.addRow("Fall Status", self.fallStatus)
        formLayot.addRow("", self.emergencyButton)
        formLayot.addRow("", self.resetButton)
        
        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("Fall Detection Sensor") 
        
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
            self.fallStatus.setText('EMERGENCY DETECTED')
            self.fallStatus.setStyleSheet("color: red")
        elif 'Normal' in messg:
            self.fallStatus.setText('Normal')
            self.fallStatus.setStyleSheet("color: green")
            
    def simulate_fall(self):
        # Simulate fall detection with high acceleration values
        accel_x = random.uniform(3.0, 5.0)
        accel_y = random.uniform(2.0, 4.0)
        accel_z = random.uniform(1.0, 3.0)
        
        self.accelerationX.setText(f"{accel_x:.2f}")
        self.accelerationY.setText(f"{accel_y:.2f}")
        self.accelerationZ.setText(f"{accel_z:.2f}")
        
        # Calculate total acceleration magnitude
        total_accel = math.sqrt(accel_x**2 + accel_y**2 + accel_z**2)
        
        if total_accel > FALL_ACCELERATION_THRESHOLD:
            self.fallStatus.setText('FALL DETECTED!')
            self.fallStatus.setStyleSheet("color: red")
            current_data = f'EMERGENCY: Fall detected! Acceleration: {total_accel:.2f}g, X:{accel_x:.2f}, Y:{accel_y:.2f}, Z:{accel_z:.2f}'
            self.mc.publish_to(self.ePublisherTopic.text(), current_data)
    
    def reset_status(self):
        """Reset fall detection status to normal"""
        try:
            self.fallStatus.setText('Normal')
            self.fallStatus.setStyleSheet("color: green")
            current_data = 'Reset: Fall detection status reset to normal'
            self.mc.publish_to(self.ePublisherTopic.text(), current_data)
            ic("Fall detection status reset to normal")
        except Exception as e:
            ic(f"Error resetting fall status: {e}")
            print(f"Error resetting fall status: {e}")

class MainWindow(QMainWindow):    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)        
        # Init of Mqtt_client class        
        self.mc = MC()
        
        # Creating timer for continuous monitoring
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.update_sensor_data)
        self.timer.start(1000)  # Update every second
        
        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)
        # set up main window
        self.setGeometry(30, 600, 400, 200)
        self.setWindowTitle('Fall Detection Sensor')
        # Init QDockWidget objects        
        self.connectionDock = ConnectionDock(self.mc)       
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)        

    def update_sensor_data(self):
        if not self.mc.connected:
            return
            
        # Simulate normal walking/movement data
        accel_x = random.uniform(-0.5, 0.5)
        accel_y = random.uniform(-0.3, 0.3)
        accel_z = random.uniform(8.5, 10.5)  # Gravity + small variations
        
        self.connectionDock.accelerationX.setText(f"{accel_x:.2f}")
        self.connectionDock.accelerationY.setText(f"{accel_y:.2f}")
        self.connectionDock.accelerationZ.setText(f"{accel_z:.2f}")
        
        # Calculate total acceleration magnitude
        total_accel = math.sqrt(accel_x**2 + accel_y**2 + accel_z**2)
        
        # Normal movement data
        current_data = f'Normal: Acceleration: {total_accel:.2f}g, X:{accel_x:.2f}, Y:{accel_y:.2f}, Z:{accel_z:.2f}'
        self.mc.publish_to(fall_topic, current_data)

if __name__ == '__main__':
    try:    
        app = QApplication(sys.argv)
        mainwin = MainWindow()
        mainwin.show()
        app.exec_()
    except Exception as e:
        print(f"Error: {e}")

# Emergency Button Emulator for Elderly Care Smart Home
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

# Creating Client name - should be unique 
global clientname, CONNECTED
CONNECTED = False
r = random.randrange(1, 10000000)
clientname = "EmergencyButton_" + str(r)
emergency_topic = comm_topic + 'sensors/emergency_button'

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
    """Emergency Button Connection Dock"""
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
        
        # Emergency button display
        self.ePublisherTopic = QLineEdit()
        self.ePublisherTopic.setText(emergency_topic)
        
        self.emergencyButton = QPushButton("🚨 EMERGENCY HELP! 🚨", self)
        self.emergencyButton.setToolTip("Press in case of emergency")
        self.emergencyButton.clicked.connect(self.trigger_emergency)
        self.emergencyButton.setStyleSheet("background-color: red; font-size: 16px; font-weight: bold; color: white; padding: 20px;")
        self.emergencyButton.setMinimumHeight(80)
        
        self.statusDisplay = QLineEdit()
        self.statusDisplay.setText('Ready')
        self.statusDisplay.setStyleSheet("color: green; font-size: 14px;")
        self.statusDisplay.setReadOnly(True)
        
        self.lastPressed = QLineEdit()
        self.lastPressed.setText('Never')
        self.lastPressed.setReadOnly(True)
        
        self.emergencyCount = QLineEdit()
        self.emergencyCount.setText('0')
        self.emergencyCount.setReadOnly(True)
        
        self.resetButton = QPushButton("Reset Status", self)
        self.resetButton.setToolTip("Reset emergency status")
        self.resetButton.clicked.connect(self.reset_status)
        self.resetButton.setStyleSheet("background-color: orange")
        
        formLayot = QFormLayout()
        formLayot.addRow("Turn On/Off", self.eConnectbtn)
        formLayot.addRow("Pub topic", self.ePublisherTopic)
        formLayot.addRow("", self.emergencyButton)
        formLayot.addRow("Status", self.statusDisplay)
        formLayot.addRow("Last Pressed", self.lastPressed)
        formLayot.addRow("Emergency Count", self.emergencyCount)
        formLayot.addRow("", self.resetButton)
        
        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("Emergency Button") 
        
        # Initialize counters
        self.emergency_press_count = 0
        
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
            self.statusDisplay.setText('EMERGENCY ACTIVE')
            self.statusDisplay.setStyleSheet("color: red; font-size: 14px;")
        elif 'Reset' in messg:
            self.statusDisplay.setText('Ready')
            self.statusDisplay.setStyleSheet("color: green; font-size: 14px;")
            
    def trigger_emergency(self):
        self.emergency_press_count += 1
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        self.statusDisplay.setText('EMERGENCY TRIGGERED!')
        self.statusDisplay.setStyleSheet("color: red; font-size: 14px;")
        self.lastPressed.setText(current_time)
        self.emergencyCount.setText(str(self.emergency_press_count))
        
        # Change button appearance to show it's been pressed
        self.emergencyButton.setStyleSheet("background-color: darkred; font-size: 16px; font-weight: bold; color: white; padding: 20px;")
        
        current_data = f'EMERGENCY: Emergency button pressed at {current_time}! Press count: {self.emergency_press_count}'
        self.mc.publish_to(self.ePublisherTopic.text(), current_data)
        
        # Flash the button to show it was pressed
        self.flash_button()
        
    def reset_status(self):
        self.statusDisplay.setText('Ready')
        self.statusDisplay.setStyleSheet("color: green; font-size: 14px;")
        self.emergencyButton.setStyleSheet("background-color: red; font-size: 16px; font-weight: bold; color: white; padding: 20px;")
        
        current_data = 'Reset: Emergency status reset'
        self.mc.publish_to(self.ePublisherTopic.text(), current_data)
        
    def flash_button(self):
        # Create a simple flash effect
        original_style = self.emergencyButton.styleSheet()
        self.emergencyButton.setStyleSheet("background-color: yellow; font-size: 16px; font-weight: bold; color: black; padding: 20px;")
        
        # Reset after 500ms
        QTimer.singleShot(500, lambda: self.emergencyButton.setStyleSheet(original_style))

class MainWindow(QMainWindow):    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)        
        # Init of Mqtt_client class        
        self.mc = MC()
        
        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)
        # set up main window
        self.setGeometry(30, 200, 400, 250)
        self.setWindowTitle('Emergency Button')
        # Init QDockWidget objects        
        self.connectionDock = ConnectionDock(self.mc)       
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)        

if __name__ == '__main__':
    try:    
        app = QApplication(sys.argv)
        mainwin = MainWindow()
        mainwin.show()
        app.exec_()
    except Exception as e:
        print(f"Error: {e}")

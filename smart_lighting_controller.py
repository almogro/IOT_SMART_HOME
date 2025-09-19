# Smart Lighting Controller Emulator for Elderly Care Smart Home
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
clientname = "SmartLighting_" + str(r)
lighting_topic = comm_topic + 'actuators/smart_lighting'

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
    """Smart Lighting Controller Connection Dock"""
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
        
        # Lighting control display
        self.eSubscribeTopic = QLineEdit()
        self.eSubscribeTopic.setText(lighting_topic + '/control')
        
        self.ePublisherTopic = QLineEdit()
        self.ePublisherTopic.setText(lighting_topic + '/status')
        
        # Room lighting controls
        self.livingRoomLight = QPushButton("Living Room Light", self)
        self.livingRoomLight.clicked.connect(lambda: self.toggle_light("Living Room"))
        self.livingRoomLight.setStyleSheet("background-color: gray")
        
        self.bedroomLight = QPushButton("Bedroom Light", self)
        self.bedroomLight.clicked.connect(lambda: self.toggle_light("Bedroom"))
        self.bedroomLight.setStyleSheet("background-color: gray")
        
        self.bathroomLight = QPushButton("Bathroom Light", self)
        self.bathroomLight.clicked.connect(lambda: self.toggle_light("Bathroom"))
        self.bathroomLight.setStyleSheet("background-color: gray")
        
        self.kitchenLight = QPushButton("Kitchen Light", self)
        self.kitchenLight.clicked.connect(lambda: self.toggle_light("Kitchen"))
        self.kitchenLight.setStyleSheet("background-color: gray")
        
        # Emergency lighting
        self.emergencyLight = QPushButton("🚨 EMERGENCY LIGHTING 🚨", self)
        self.emergencyLight.clicked.connect(self.activate_emergency_lighting)
        self.emergencyLight.setStyleSheet("background-color: red; font-size: 14px; font-weight: bold; color: white;")
        
        # Reset button
        self.resetLights = QPushButton("Reset All Lights", self)
        self.resetLights.clicked.connect(self.reset_all_lights)
        self.resetLights.setStyleSheet("background-color: orange; font-weight: bold")
        
        # Status display
        self.statusDisplay = QTextEdit()
        self.statusDisplay.setMaximumHeight(100)
        self.statusDisplay.setReadOnly(True)
        self.statusDisplay.setText("All lights OFF")
        
        # Brightness control
        self.brightnessSlider = QSlider(Qt.Horizontal)
        self.brightnessSlider.setMinimum(0)
        self.brightnessSlider.setMaximum(100)
        self.brightnessSlider.setValue(50)
        self.brightnessSlider.valueChanged.connect(self.update_brightness)
        
        self.brightnessLabel = QLabel("Brightness: 50%")
        
        # Auto mode toggle
        self.autoModeCheckbox = QCheckBox("Auto Mode (Motion Detection)")
        self.autoModeCheckbox.stateChanged.connect(self.toggle_auto_mode)
        
        formLayot = QFormLayout()
        formLayot.addRow("Turn On/Off", self.eConnectbtn)
        formLayot.addRow("Sub topic", self.eSubscribeTopic)
        formLayot.addRow("Pub topic", self.ePublisherTopic)
        formLayot.addRow("", self.livingRoomLight)
        formLayot.addRow("", self.bedroomLight)
        formLayot.addRow("", self.bathroomLight)
        formLayot.addRow("", self.kitchenLight)
        formLayot.addRow("", self.emergencyLight)
        formLayot.addRow("", self.resetLights)
        formLayot.addRow("Status", self.statusDisplay)
        formLayot.addRow("Brightness", self.brightnessSlider)
        formLayot.addRow("", self.brightnessLabel)
        formLayot.addRow("", self.autoModeCheckbox)
        
        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("Smart Lighting Controller") 
        
        # Initialize lighting states
        self.light_states = {
            "Living Room": False,
            "Bedroom": False,
            "Bathroom": False,
            "Kitchen": False
        }
        self.auto_mode = False
        
    def on_connected(self):
        self.eConnectbtn.setStyleSheet("background-color: green")
        # Subscribe to control messages
        self.mc.subscribe_to(self.eSubscribeTopic.text())
                    
    def on_button_connect_click(self):
        self.mc.set_broker(self.eHostInput.text())
        self.mc.set_port(int(self.ePort.text()))
        self.mc.set_clientName(self.eClientID.text())
        self.mc.set_username(self.eUserName.text())
        self.mc.set_password(self.ePassword.text())        
        self.mc.connect_to()        
        self.mc.start_listening()
        
    def update_btn_state(self, messg):
        try:
            if 'Turn On' in messg and 'Living Room' in messg:
                self.light_states["Living Room"] = True
                self.livingRoomLight.setStyleSheet("background-color: yellow")
            elif 'Turn Off' in messg and 'Living Room' in messg:
                self.light_states["Living Room"] = False
                self.livingRoomLight.setStyleSheet("background-color: gray")
            elif 'Emergency' in messg:
                self.activate_emergency_lighting()
            elif 'Auto Mode' in messg:
                self.autoModeCheckbox.setChecked(True)
            ic(f"Updated button state for message: {messg}")
        except Exception as e:
            ic(f"Error updating button state: {e}")
            print(f"Error updating button state: {e}")
            
    def toggle_light(self, room):
        try:
            self.light_states[room] = not self.light_states[room]
            
            # Convert room name to proper attribute name
            room_attr = room.replace(" ", "")
            room_attr = room_attr[0].lower() + room_attr[1:] + "Light"
            
            if self.light_states[room]:
                getattr(self, room_attr).setStyleSheet("background-color: yellow")
                action = "ON"
            else:
                getattr(self, room_attr).setStyleSheet("background-color: gray")
                action = "OFF"
                
            current_data = f'Turn {action} {room} light'
            self.mc.publish_to(self.ePublisherTopic.text(), current_data)
            self.update_status_display()
            ic(f"Toggled {room} light to {action}")
            
        except Exception as e:
            ic(f"Error toggling light {room}: {e}")
            print(f"Error toggling light {room}: {e}")
        
    def activate_emergency_lighting(self):
        try:
            # Turn on all lights for emergency
            for room in self.light_states:
                self.light_states[room] = True
                # Convert room name to proper attribute name
                room_attr = room.replace(" ", "")
                room_attr = room_attr[0].lower() + room_attr[1:] + "Light"
                getattr(self, room_attr).setStyleSheet("background-color: red")
                
            self.emergencyLight.setStyleSheet("background-color: darkred; font-size: 14px; font-weight: bold; color: white;")
            
            current_data = 'EMERGENCY: All lights activated for emergency!'
            self.mc.publish_to(self.ePublisherTopic.text(), current_data)
            self.update_status_display()
            ic("Emergency lighting activated")
            
        except Exception as e:
            ic(f"Error in emergency lighting: {e}")
            print(f"Error in emergency lighting: {e}")
    
    def reset_all_lights(self):
        """Reset all lights to OFF state"""
        try:
            for room in self.light_states:
                self.light_states[room] = False
                # Convert room name to proper attribute name
                room_attr = room.replace(" ", "")
                room_attr = room_attr[0].lower() + room_attr[1:] + "Light"
                getattr(self, room_attr).setStyleSheet("background-color: gray")
                
            self.emergencyLight.setStyleSheet("background-color: red; font-size: 14px; font-weight: bold; color: white;")
            
            current_data = 'Reset: All lights turned OFF'
            self.mc.publish_to(self.ePublisherTopic.text(), current_data)
            self.update_status_display()
            ic("All lights reset to OFF")
            
        except Exception as e:
            ic(f"Error resetting lights: {e}")
            print(f"Error resetting lights: {e}")
        
    def update_brightness(self, value):
        self.brightnessLabel.setText(f"Brightness: {value}%")
        current_data = f'Brightness: Set to {value}%'
        self.mc.publish_to(self.ePublisherTopic.text(), current_data)
        
    def toggle_auto_mode(self, state):
        self.auto_mode = state == 2  # Qt.Checked
        if self.auto_mode:
            current_data = 'Auto Mode: Motion detection enabled'
        else:
            current_data = 'Auto Mode: Motion detection disabled'
        self.mc.publish_to(self.ePublisherTopic.text(), current_data)
        
    def update_status_display(self):
        status_text = "Light Status:\n"
        for room, state in self.light_states.items():
            status = "ON" if state else "OFF"
            status_text += f"{room}: {status}\n"
        self.statusDisplay.setText(status_text)

class MainWindow(QMainWindow):    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)        
        # Init of Mqtt_client class        
        self.mc = MC()
        
        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)
        # set up main window
        self.setGeometry(30, 100, 400, 350)
        self.setWindowTitle('Smart Lighting Controller')
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

# Medication Reminder System for Elderly Care Smart Home
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
clientname = "MedicationReminder_" + str(r)
medication_topic = comm_topic + 'sensors/medication_reminder'

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
    """Medication Reminder Connection Dock"""
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
        
        # Medication reminder display
        self.ePublisherTopic = QLineEdit()
        self.ePublisherTopic.setText(medication_topic)
        
        # Medication schedule
        self.medicationList = QListWidget()
        self.medicationList.addItem("Morning: Blood Pressure (8:00 AM)")
        self.medicationList.addItem("Afternoon: Heart Medicine (2:00 PM)")
        self.medicationList.addItem("Evening: Vitamins (8:00 PM)")
        self.medicationList.addItem("Night: Sleep Aid (10:00 PM)")
        
        # Status display
        self.statusDisplay = QLineEdit()
        self.statusDisplay.setText('System Ready')
        self.statusDisplay.setStyleSheet("color: green")
        self.statusDisplay.setReadOnly(True)
        
        # Next medication
        self.nextMedication = QLineEdit()
        self.nextMedication.setText('Blood Pressure - 8:00 AM')
        self.nextMedication.setReadOnly(True)
        
        # Time until next dose
        self.timeUntilNext = QLineEdit()
        self.timeUntilNext.setText('2 hours 15 minutes')
        self.timeUntilNext.setReadOnly(True)
        
        # Control buttons
        self.takeMedicationButton = QPushButton("✅ Take Medication", self)
        self.takeMedicationButton.setToolTip("Mark medication as taken")
        self.takeMedicationButton.clicked.connect(self.take_medication)
        self.takeMedicationButton.setStyleSheet("background-color: green")
        
        self.skipMedicationButton = QPushButton("⏭️ Skip Medication", self)
        self.skipMedicationButton.setToolTip("Skip this medication")
        self.skipMedicationButton.clicked.connect(self.skip_medication)
        self.skipMedicationButton.setStyleSheet("background-color: orange")
        
        self.emergencyButton = QPushButton("🚨 MISSED MEDICATION ALERT 🚨", self)
        self.emergencyButton.setToolTip("Alert for missed medication")
        self.emergencyButton.clicked.connect(self.alert_missed_medication)
        self.emergencyButton.setStyleSheet("background-color: red")
        
        self.resetButton = QPushButton("Reset Status", self)
        self.resetButton.setToolTip("Reset medication reminder status")
        self.resetButton.clicked.connect(self.reset_status)
        self.resetButton.setStyleSheet("background-color: orange")
        
        # Medication compliance meter
        self.complianceMeter = QProgressBar()
        self.complianceMeter.setValue(85)
        self.complianceMeter.setMaximum(100)
        
        self.complianceLabel = QLabel("Compliance: 85%")
        
        formLayot = QFormLayout()
        formLayot.addRow("Turn On/Off", self.eConnectbtn)
        formLayot.addRow("Pub topic", self.ePublisherTopic)
        formLayot.addRow("Medication Schedule", self.medicationList)
        formLayot.addRow("Status", self.statusDisplay)
        formLayot.addRow("Next Medication", self.nextMedication)
        formLayot.addRow("Time Until Next", self.timeUntilNext)
        formLayot.addRow("", self.takeMedicationButton)
        formLayot.addRow("", self.skipMedicationButton)
        formLayot.addRow("", self.emergencyButton)
        formLayot.addRow("", self.resetButton)
        formLayot.addRow("Compliance", self.complianceMeter)
        formLayot.addRow("", self.complianceLabel)
        
        widget = QWidget(self)
        widget.setLayout(formLayot)
        self.setTitleBarWidget(widget)
        self.setWidget(widget)     
        self.setWindowTitle("Medication Reminder System") 
        
        # Initialize medication tracking
        self.medication_taken = {
            "Morning": False,
            "Afternoon": False,
            "Evening": False,
            "Night": False
        }
        self.compliance_score = 85
        
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
        if 'Taken' in messg:
            self.statusDisplay.setText('Medication Taken')
            self.statusDisplay.setStyleSheet("color: green")
        elif 'Skipped' in messg:
            self.statusDisplay.setText('Medication Skipped')
            self.statusDisplay.setStyleSheet("color: orange")
        elif 'Missed' in messg:
            self.statusDisplay.setText('Medication Missed!')
            self.statusDisplay.setStyleSheet("color: red")
            
    def take_medication(self):
        current_time = datetime.datetime.now().strftime("%H:%M")
        current_data = f'Medication Taken: Medication taken at {current_time}'
        self.mc.publish_to(self.ePublisherTopic.text(), current_data)
        
        self.statusDisplay.setText('Medication Taken')
        self.statusDisplay.setStyleSheet("color: green")
        
        # Update compliance
        self.compliance_score = min(100, self.compliance_score + 2)
        self.complianceMeter.setValue(self.compliance_score)
        self.complianceLabel.setText(f"Compliance: {self.compliance_score}%")
        
    def skip_medication(self):
        current_time = datetime.datetime.now().strftime("%H:%M")
        current_data = f'Medication Skipped: Medication skipped at {current_time}'
        self.mc.publish_to(self.ePublisherTopic.text(), current_data)
        
        self.statusDisplay.setText('Medication Skipped')
        self.statusDisplay.setStyleSheet("color: orange")
        
        # Update compliance
        self.compliance_score = max(0, self.compliance_score - 5)
        self.complianceMeter.setValue(self.compliance_score)
        self.complianceLabel.setText(f"Compliance: {self.compliance_score}%")
        
    def alert_missed_medication(self):
        current_time = datetime.datetime.now().strftime("%H:%M")
        current_data = f'EMERGENCY: Medication missed! Alert sent at {current_time}'
        self.mc.publish_to(self.ePublisherTopic.text(), current_data)
        
        self.statusDisplay.setText('MISSED MEDICATION ALERT!')
        self.statusDisplay.setStyleSheet("color: red")
        
        # Update compliance
        self.compliance_score = max(0, self.compliance_score - 10)
        self.complianceMeter.setValue(self.compliance_score)
        self.complianceLabel.setText(f"Compliance: {self.compliance_score}%")
    
    def reset_status(self):
        """Reset medication reminder status to normal"""
        try:
            self.statusDisplay.setText('System Ready')
            self.statusDisplay.setStyleSheet("color: green")
            
            # Reset compliance to good level
            self.compliance_score = 85
            self.complianceMeter.setValue(self.compliance_score)
            self.complianceLabel.setText(f"Compliance: {self.compliance_score}%")
            
            current_data = 'Reset: Medication reminder status reset to normal'
            self.mc.publish_to(self.ePublisherTopic.text(), current_data)
            ic("Medication reminder status reset to normal")
        except Exception as e:
            ic(f"Error resetting medication status: {e}")
            print(f"Error resetting medication status: {e}")

class MainWindow(QMainWindow):    
    def __init__(self, parent=None):
        QMainWindow.__init__(self, parent)        
        # Init of Mqtt_client class        
        self.mc = MC()
        
        # Creating timer for medication reminders
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(self.check_medication_schedule)
        self.timer.start(60000)  # Check every minute
        
        # general GUI settings
        self.setUnifiedTitleAndToolBarOnMac(True)
        # set up main window
        self.setGeometry(30, 50, 450, 400)
        self.setWindowTitle('Medication Reminder System')
        # Init QDockWidget objects        
        self.connectionDock = ConnectionDock(self.mc)       
        self.addDockWidget(Qt.TopDockWidgetArea, self.connectionDock)        

    def check_medication_schedule(self):
        if not self.mc.connected:
            return
            
        current_hour = datetime.datetime.now().hour
        
        # Check for medication times
        if current_hour == 8:  # Morning medication
            current_data = 'Reminder: Morning medication due - Blood Pressure'
            self.mc.publish_to(medication_topic, current_data)
        elif current_hour == 14:  # Afternoon medication
            current_data = 'Reminder: Afternoon medication due - Heart Medicine'
            self.mc.publish_to(medication_topic, current_data)
        elif current_hour == 20:  # Evening medication
            current_data = 'Reminder: Evening medication due - Vitamins'
            self.mc.publish_to(medication_topic, current_data)
        elif current_hour == 22:  # Night medication
            current_data = 'Reminder: Night medication due - Sleep Aid'
            self.mc.publish_to(medication_topic, current_data)

if __name__ == '__main__':
    try:    
        app = QApplication(sys.argv)
        mainwin = MainWindow()
        mainwin.show()
        app.exec_()
    except Exception as e:
        print(f"Error: {e}")

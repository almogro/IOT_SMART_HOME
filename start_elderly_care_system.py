#!/usr/bin/env python3
"""
Elderly Care Smart Home System Startup Script
This script starts all the emulators and the main GUI application
"""

import subprocess
import sys
import time
import os
from pathlib import Path

def start_emulator(script_name, description):
    """Start an emulator script in a new process"""
    try:
        print(f"Starting {description}...")
        process = subprocess.Popen([sys.executable, script_name], 
                                 stdout=subprocess.PIPE, 
                                 stderr=subprocess.PIPE)
        print(f"✓ {description} started (PID: {process.pid})")
        return process
    except Exception as e:
        print(f"✗ Failed to start {description}: {e}")
        return None

def main():
    print("=" * 60)
    print("🏠 ELDERLY CARE SMART HOME SYSTEM")
    print("=" * 60)
    print()
    
    # Get the directory where this script is located
    script_dir = Path(__file__).parent
    
    # List of emulators to start
    emulators = [
        ("fall_detection_sensor.py", "Fall Detection Sensor"),
        ("health_monitor.py", "Health Monitor"),
        ("emergency_button.py", "Emergency Button"),
        ("smart_lighting_controller.py", "Smart Lighting Controller"),
        ("medication_reminder.py", "Medication Reminder System"),
    ]
    
    # Start the data manager first
    print("Starting Data Manager...")
    manager_process = start_emulator("manager.py", "Data Manager")
    if manager_process:
        time.sleep(2)  # Give manager time to start
    
    # Start all emulators
    processes = []
    for script, description in emulators:
        process = start_emulator(script, description)
        if process:
            processes.append((process, description))
        time.sleep(1)  # Small delay between starting emulators
    
    print()
    print("=" * 60)
    print("🚀 ALL SYSTEMS STARTED")
    print("=" * 60)
    print()
    print("Starting Main GUI Application...")
    print("Close the GUI window to stop all systems.")
    print()
    
    # Start the main GUI application
    try:
        gui_process = subprocess.run([sys.executable, "gui.py"])
    except KeyboardInterrupt:
        print("\nShutting down all systems...")
    except Exception as e:
        print(f"Error running GUI: {e}")
    finally:
        # Clean up all processes
        print("Stopping all emulators...")
        for process, description in processes:
            try:
                process.terminate()
                print(f"✓ {description} stopped")
            except:
                pass
        
        if manager_process:
            try:
                manager_process.terminate()
                print("✓ Data Manager stopped")
            except:
                pass
        
        print("All systems stopped.")

if __name__ == "__main__":
    main()

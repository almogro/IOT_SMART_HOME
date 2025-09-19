#!/usr/bin/env python3
"""
Test script for Elderly Care Smart Home System
This script tests the basic functionality of the system components
"""

import sys
import os
import time
from pathlib import Path

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_imports():
    """Test if all required modules can be imported"""
    print("Testing imports...")
    
    try:
        import init
        print("✓ init.py imported successfully")
    except Exception as e:
        print(f"✗ Failed to import init.py: {e}")
        return False
    
    try:
        import agent
        print("✓ agent.py imported successfully")
    except Exception as e:
        print(f"✗ Failed to import agent.py: {e}")
        return False
    
    try:
        import data_acq
        print("✓ data_acq.py imported successfully")
    except Exception as e:
        print(f"✗ Failed to import data_acq.py: {e}")
        return False
    
    return True

def test_database():
    """Test database initialization"""
    print("\nTesting database...")
    
    try:
        import data_acq as da
        # Initialize database
        da.init_db('test_elderly_care.db')
        print("✓ Database initialized successfully")
        
        # Test adding data
        da.add_sensor_data('TestDevice', 'sensor', 'Test Value', 'normal', 'Test Location')
        print("✓ Sensor data added successfully")
        
        # Test fetching data
        data = da.fetch_sensor_data()
        print(f"✓ Fetched {len(data)} records from database")
        
        # Clean up test database
        os.remove('test_elderly_care.db')
        print("✓ Test database cleaned up")
        
        return True
    except Exception as e:
        print(f"✗ Database test failed: {e}")
        return False

def test_mqtt_client():
    """Test MQTT client creation"""
    print("\nTesting MQTT client...")
    
    try:
        from agent import Mqtt_client
        client = Mqtt_client()
        print("✓ MQTT client created successfully")
        
        # Test setters
        client.set_broker('test.mosquitto.org')
        client.set_port(1883)
        client.set_clientName('test_client')
        print("✓ MQTT client configuration successful")
        
        return True
    except Exception as e:
        print(f"✗ MQTT client test failed: {e}")
        return False

def test_emulator_imports():
    """Test if emulator modules can be imported"""
    print("\nTesting emulator imports...")
    
    emulators = [
        'fall_detection_sensor',
        'health_monitor', 
        'emergency_button',
        'smart_lighting_controller',
        'medication_reminder'
    ]
    
    all_imported = True
    for emulator in emulators:
        try:
            __import__(emulator)
            print(f"✓ {emulator}.py imported successfully")
        except Exception as e:
            print(f"✗ Failed to import {emulator}.py: {e}")
            all_imported = False
    
    return all_imported

def test_gui_import():
    """Test GUI module import"""
    print("\nTesting GUI import...")
    
    try:
        import gui
        print("✓ gui.py imported successfully")
        return True
    except Exception as e:
        print(f"✗ Failed to import gui.py: {e}")
        return False

def main():
    """Run all tests"""
    print("=" * 60)
    print("🧪 ELDERLY CARE SMART HOME SYSTEM - TEST SUITE")
    print("=" * 60)
    
    tests = [
        ("Import Tests", test_imports),
        ("Database Tests", test_database),
        ("MQTT Client Tests", test_mqtt_client),
        ("Emulator Import Tests", test_emulator_imports),
        ("GUI Import Tests", test_gui_import)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
            print(f"✓ {test_name} PASSED")
        else:
            print(f"✗ {test_name} FAILED")
    
    print("\n" + "=" * 60)
    print(f"📊 TEST RESULTS: {passed}/{total} tests passed")
    print("=" * 60)
    
    if passed == total:
        print("🎉 ALL TESTS PASSED! System is ready to run.")
        print("\nTo start the system, run:")
        print("python start_elderly_care_system.py")
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())

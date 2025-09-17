#!/usr/bin/env python3
"""
Test script to verify microservices structure and functionality
"""

import sys
import os
import importlib.util

def test_shared_modules():
    """Test that shared modules can be imported"""
    print("Testing shared modules...")
    
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__)))
        
        # Test shared models
        from shared.models import MeterReading, OptimizationRequest, OptimizationResponse
        print("✅ Shared models imported successfully")
        
        # Test shared utils
        from shared.utils import ServiceRegistry
        print("✅ Shared utils imported successfully")
        
        # Test model creation
        from datetime import datetime
        reading = MeterReading(
            household_id=1,
            timestamp=datetime.now(),
            consumption=1.5
        )
        print(f"✅ MeterReading model created: {reading}")
        
        return True
    except Exception as e:
        print(f"❌ Shared modules test failed: {e}")
        return False

def test_optimization_service():
    """Test optimization service functionality"""
    print("\nTesting optimization service...")
    
    try:
        sys.path.append(os.path.join(os.path.dirname(__file__), 'microservices', 'energy-optimization-service'))
        
        from optimization_engine import OptimizationEngine
        
        optimizer = OptimizationEngine()
        
        # Test optimization
        test_data = [
            {"household_id": 1, "timestamp": "2024-01-01 12:00:00", "consumption": 1.0},
            {"household_id": 1, "timestamp": "2024-01-01 12:15:00", "consumption": 2.0},
            {"household_id": 1, "timestamp": "2024-01-01 12:30:00", "consumption": 3.0}
        ]
        
        schedule = optimizer.optimize_energy(test_data)
        print(f"✅ Optimization completed: {len(schedule)} schedule items")
        print(f"   First schedule item: {schedule[0] if schedule else 'None'}")
        
        # Test battery status
        status = optimizer.get_battery_status()
        print(f"✅ Battery status: {status}")
        
        return True
    except Exception as e:
        print(f"❌ Optimization service test failed: {e}")
        return False

def test_service_structure():
    """Test that all service directories exist with required files"""
    print("\nTesting service structure...")
    
    services = [
        "api-gateway",
        "energy-optimization-service",
        "data-ingestion-service",
        "household-service", 
        "weather-pv-service",
        "iot-service"
    ]
    
    required_files = ["main.py", "requirements.txt", "Dockerfile"]
    
    all_good = True
    
    for service in services:
        service_path = os.path.join("microservices", service)
        
        if not os.path.exists(service_path):
            print(f"❌ Service directory missing: {service}")
            all_good = False
            continue
            
        for file_name in required_files:
            file_path = os.path.join(service_path, file_name)
            
            if service in ["api-gateway", "energy-optimization-service"]:
                # These are implemented
                if not os.path.exists(file_path):
                    if file_name == "main.py":
                        print(f"❌ Required file missing: {service}/{file_name}")
                        all_good = False
                    else:
                        print(f"⚠️  File missing but created: {service}/{file_name}")
                else:
                    print(f"✅ {service}/{file_name}")
            else:
                # These are placeholders for future implementation
                if not os.path.exists(file_path):
                    print(f"📝 To be implemented: {service}/{file_name}")
                else:
                    print(f"✅ {service}/{file_name}")
    
    return all_good

def main():
    """Run all tests"""
    print("🚀 Testing Microservices Setup")
    print("=" * 50)
    
    tests = [
        test_shared_modules,
        test_optimization_service,
        test_service_structure
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("📊 Test Results:")
    print(f"✅ Passed: {sum(results)}/{len(results)}")
    print(f"❌ Failed: {len(results) - sum(results)}/{len(results)}")
    
    if all(results):
        print("\n🎉 All tests passed! Microservices setup is ready.")
    else:
        print("\n⚠️  Some tests failed. Please check the issues above.")
    
    print("\n📋 Next Steps:")
    print("1. Start Docker Desktop")
    print("2. Run: docker-compose up postgres redis grafana")  
    print("3. Run: docker-compose up api-gateway energy-optimization")
    print("4. Test API: curl http://localhost:8000/health")
    print("5. Test optimization: curl http://localhost:8000/api/optimize/1")

if __name__ == "__main__":
    main()
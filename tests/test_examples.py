#!/usr/bin/env python3
"""Test runner for example files."""

import os
import sys
import asyncio
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Add package to path
sys.path.insert(0, str(Path(__file__).parent))

def test_simple_invoice():
    """Test the simple invoice example."""
    print("\n" + "="*60)
    print("Testing: simple_invoice.py")
    print("="*60)
    
    try:
        # Import and run the example
        from examples import simple_invoice
        asyncio.run(simple_invoice.main())
        print("✅ Simple invoice example completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Simple invoice example failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_comprehensive_example():
    """Test the comprehensive example."""
    print("\n" + "="*60)
    print("Testing: comprehensive_example.py")
    print("="*60)
    
    try:
        # Import and run the example
        from examples import comprehensive_example
        asyncio.run(comprehensive_example.main())
        print("✅ Comprehensive example completed successfully!")
        return True
    except Exception as e:
        print(f"❌ Comprehensive example failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("🔧 Testing FIRS E-Invoice Python Examples")
    print("="*60)
    
    # Verify environment
    service_id = os.environ.get('FIRS_SERVICE_ID')
    api_key = os.environ.get('FIRS_API_KEY')
    
    print("\n📌 Environment Check:")
    print(f"   FIRS_SERVICE_ID: {'✅ Found' if service_id else '❌ Not found'}")
    print(f"   FIRS_API_KEY: {'✅ Found' if api_key else '❌ Not found'}")
    
    if not service_id:
        print("\n⚠️  Warning: FIRS_SERVICE_ID not found in environment")
        print("   IRN generation will use fallback values")
    
    results = []
    
    # Test simple invoice
    results.append(("Simple Invoice", test_simple_invoice()))
    
    # Test comprehensive example  
    results.append(("Comprehensive Example", test_comprehensive_example()))
    
    # Summary
    print("\n" + "="*60)
    print("TEST SUMMARY")
    print("="*60)
    for name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{name}: {status}")
    
    # Overall result
    all_passed = all(result[1] for result in results)
    print("\n" + "="*60)
    if all_passed:
        print("🎉 All examples passed successfully!")
    else:
        print("⚠️  Some examples failed. Check the output above.")
    
    sys.exit(0 if all_passed else 1)
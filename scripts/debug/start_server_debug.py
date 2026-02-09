"""
Start the FastAPI server with debug output
"""

import sys
import traceback

try:
    print("=" * 70)
    print("  STARTING FASTAPI SERVER WITH DEBUG MODE")
    print("=" * 70)
    
    print("\n📦 Importing FastAPI app...")
    from app.main import app
    print("✅ App imported successfully!")
    
    print("\n🚀 Starting uvicorn server...")
    print("   URL: http://127.0.0.1:8000")
    print("   Docs: http://127.0.0.1:8000/docs")
    print("\n" + "=" * 70)
    
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
    
except ImportError as e:
    print("\n❌ IMPORT ERROR:")
    print(f"   {e}")
    print("\n📋 Traceback:")
    traceback.print_exc()
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    print("\n📋 Traceback:")
    traceback.print_exc()
    sys.exit(1)

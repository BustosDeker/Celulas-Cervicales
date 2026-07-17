
import sys
print("Python executable:", sys.executable)
print("\nPython path:")
for p in sys.path:
    print(f"  {p}")
try:
    import flask
    print("\nFlask imported successfully!")
    print(f"Flask version: {flask.__version__}")
    print(f"Flask location: {flask.__file__}")
except Exception as e:
    print(f"\nError importing flask: {e}")

import sys
import os

print("Python executable:", sys.executable)
print("Python version:", sys.version)
print("Sys.path:")
for p in sys.path:
    print("  -", p)

try:
    import packaging
    print("\npackaging module found at:", packaging.__file__)
except ImportError as e:
    print("\nError importing packaging:", e)

print("\nChecking environment variables:")
for key, value in os.environ.items():
    if "PATH" in key.upper() or "PYTHON" in key.upper():
        print(f"{key}={value}") 
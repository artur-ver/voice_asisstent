import os
for root, dirs, files in os.walk('/'):
    if 'python' in dirs:
        print(f"Python file(s) found in {root}")
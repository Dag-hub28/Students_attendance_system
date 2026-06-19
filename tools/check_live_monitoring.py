import traceback
import sys
import os
# Ensure project root is on sys.path when running from tools/
proj_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)

try:
    import live_monitoring
    print('OK')
except Exception:
    traceback.print_exc()

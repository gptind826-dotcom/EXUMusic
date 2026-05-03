#
# Copyright (C) 2021-2022 by EXUTeam@Github, < https://github.com/EXUTeam >.
# This file is part of < https://github.com/EXUTeam/EXUMusic > project,
# and is released under the "GNU v3.0 License Agreement".
# Please see < https://github.com/EXUTeam/EXUMusic/blob/master/LICENSE >
#
# All rights reserved.

import sys
import threading

print("🚀 Starting EXU Music Bot...")


def run_flask():
    try:
        import os
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), "web"))
        from flask_dashboard import app as flask_app
        port = int(os.environ.get("PORT", 5000))
        flask_app.run(host="0.0.0.0", port=port, debug=False, use_reloader=False)
    except Exception as e:
        print(f"⚠️  Flask dashboard failed to start: {e}")


flask_thread = threading.Thread(target=run_flask, daemon=True)
flask_thread.start()
print("🌐 EXU Music Dashboard started on port 8080")

try:
    import runpy
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), "web"))
    runpy.run_module("AloneMusic", run_name="__main__")
except Exception as e:
    print("❌ Bot crashed with error:", e)
    sys.exit(1)

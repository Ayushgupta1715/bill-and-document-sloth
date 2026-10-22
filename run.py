"""One-click launcher for Bill & Document Sloth.
Starts the local server and opens your browser.
"""

import sys
import webbrowser
import threading
import time
import uvicorn

BANNER = r"""
  .---.
 /     \    🦥 BILL & DOCUMENT SLOTH
| () () |   "Stop sorting paperwork. Start living."
 \  -  /    Hacktoberfest Week 3 — Slow and Steady
  `---`     100% Local-First AI Document Manager
"""

def open_browser():
    time.sleep(1.2)
    url = "http://127.0.0.1:8000"
    print(f"\n[Sloth] Opening {url} in your browser...")
    webbrowser.open(url)

if __name__ == "__main__":
    print(BANNER)
    print("[Sloth] Initializing local database and document pipelines...")
    
    # Launch browser in a background thread
    threading.Thread(target=open_browser, daemon=True).start()
    
    # Run uvicorn server
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=False)

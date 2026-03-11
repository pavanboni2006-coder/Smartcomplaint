import urllib.request
import urllib.error
import time
import threading

# run app in a thread
import app


def run_app():
    app.app.run(port=5000, use_reloader=False)


threading.Thread(target=run_app, daemon=True).start()
time.sleep(2)

urls = [
    "http://localhost:5000/",
    "http://localhost:5000/register",
    "http://localhost:5000/login",
    "http://localhost:5000/admin/login",
]

for url in urls:
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as response:
            print(f"OK: {url} - {response.status}")
    except urllib.error.HTTPError as e:
        print(f"Error: {url} - {e.code}")
    except Exception as e:
        print(f"Failed: {url} - {e}")

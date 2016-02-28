import sys
import threading
import time
from datetime import datetime

import requests
import alexandra

app = alexandra.Application()


@app.launch
def launch(session):
    return alexandra.respond(text="I'm a fried chicken.")


@app.intent("StandUp")
def stand_up(slots, session):
    return alexandra.respond(text="please stand up, please stand up")

if __name__ == '__main__':
    def runner(): app.run('127.0.0.1', 8080,
                          debug=False,
                          validate_requests=False)
    server_thread = threading.Thread(target=runner)
    server_thread.setDaemon(True)
    server_thread.start()

    # Wait for startup.
    time.sleep(2)

    # Smack it.
    r = requests.post('http://127.0.0.1:8080', json={
        "version": "1.0",
        "session": {},
        "request": {
            "type": "LaunchRequest",
            "requestId": "request.id.string",
            "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
        }
    })

    print(r.text)

    if r.status_code is not 200:
        print("FAILWHALE")
        sys.exit(1)
    else:
        print("Success!")
        sys.exit(0)

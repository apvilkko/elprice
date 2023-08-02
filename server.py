from http.server import BaseHTTPRequestHandler, HTTPServer
from pagegen import generate
from datetime import datetime, timedelta

hostName = "0.0.0.0"
serverPort = 8234

lastFetch = None
result = None

def should_fetch(now: datetime, lastFetch: datetime):
    return (now - lastFetch) > timedelta(hours=1)

class MyServer(BaseHTTPRequestHandler):
    def do_GET(self):
        global lastFetch
        global result
        now = datetime.utcnow()
        if not result or should_fetch(now, lastFetch):
            print("Generating page")
            try:
                result = bytes(generate(), "utf-8")
                lastFetch = datetime.utcnow()
                self.send_result()
            except Exception as e:
                print(e)
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(bytes("Could not fetch data: " + str(e), "utf-8"))
        else:
            self.send_result()

    def send_result(self):
        global result
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.end_headers()
        self.wfile.write(result)

if __name__ == "__main__":        
    webServer = HTTPServer((hostName, serverPort), MyServer)
    print("Server started http://%s:%s" % (hostName, serverPort))

    try:
        webServer.serve_forever()
    except KeyboardInterrupt:
        pass

    webServer.server_close()
    print("Server stopped.")

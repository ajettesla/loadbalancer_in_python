#!/usr/bin/env python3
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_backend_servers():
    BACKEND_SERVERS_ENV = os.getenv('BACKEND_SERVERS')
    if BACKEND_SERVERS_ENV:
        logging.info(f"Received BACKEND_SERVERS: {BACKEND_SERVERS_ENV}")
        return BACKEND_SERVERS_ENV
    else:
        logging.warning("Environment variable 'BACKEND_SERVERS' is not set.")
        return None

# Loop until BACKEND_SERVERS is set
BACKEND_SERVERS_ENV = None
while not BACKEND_SERVERS_ENV:
    BACKEND_SERVERS_ENV = get_backend_servers()
    if not BACKEND_SERVERS_ENV:
        logging.info("Waiting for 10 seconds before retrying...")
        time.sleep(10)

# Parse BACKEND_SERVERS
BACKEND_SERVERS = []
for server in BACKEND_SERVERS_ENV.split(','):
    server = server.strip()
    if not server:
        continue
    if not server.startswith(('http://', 'https://')):
        server = f"http://{server}"
    BACKEND_SERVERS.append(server)

if not BACKEND_SERVERS:
    logging.error("No valid backend servers found in 'BACKEND_SERVERS' environment variable.")
    raise ValueError("No valid backend servers found in 'BACKEND_SERVERS' environment variable.")

current_server_index = 0

class LoadBalancerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global current_server_index

        target_server = BACKEND_SERVERS[current_server_index]
        current_server_index = (current_server_index + 1) % len(BACKEND_SERVERS)

        logging.info(f"Forwarding request {self.path} to {target_server}")

        try:
            # Forward the GET request to the backend server
            headers = {key: value for key, value in self.headers.items()}
            response = requests.get(
                f"{target_server}{self.path}",
                headers=headers,
                stream=True
            )

            # Forward all headers from the backend response to the client
            self.send_response(response.status_code)
            for key, value in response.headers.items():
                # Exclude headers that could cause issues
                if key.lower() not in ['content-encoding', 'transfer-encoding', 'connection']:
                    self.send_header(key, value)
            self.end_headers()

            # Forward the response content as-is, without decoding
            for chunk in response.raw.stream(1024, decode_content=False):
                self.wfile.write(chunk)

        except requests.exceptions.RequestException as e:
            logging.error(f"Error forwarding request to {target_server}: {e}")
            # Handle backend server errors
            self.send_response(502)  # Bad Gateway
            self.end_headers()
            self.wfile.write(b"502 Bad Gateway: Backend server error")

def run_load_balancer(port=80):
    server_address = ('', port)
    httpd = HTTPServer(server_address, LoadBalancerHandler)
    logging.info(f"Load Balancer is listening on port {port}...")

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        logging.info("\nKeyboard interrupt received, shutting down the load balancer.")
        httpd.server_close()
        logging.info("Load Balancer has been shut down.")

if __name__ == "__main__":
    # Allow port to be set via environment variable; default to 80
    port = int(os.getenv('LOAD_BALANCER_PORT', 80))
    run_load_balancer(port=port)

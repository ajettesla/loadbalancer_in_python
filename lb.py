#!/usr/bin/env python3
import os
import time
from http.server import BaseHTTPRequestHandler, HTTPServer
import requests
import logging
import random

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

def parse_backend_servers(backend_servers_env):
    backend_servers = []
    weights = []
    for server_entry in backend_servers_env.split(','):
        server_entry = server_entry.strip()
        if not server_entry:
            continue

        # Split server and weight using the pipe '|' delimiter
        if '|' in server_entry:
            server, weight_str = server_entry.split('|', 1)
            server = server.strip()
            weight_str = weight_str.strip()
            try:
                weight = float(weight_str)
                if weight <= 0:
                    raise ValueError
            except ValueError:
                logging.warning(f"Invalid weight '{weight_str}' for server '{server}'. Using default weight of 1.")
                weight = 1.0
        else:
            server = server_entry
            weight = 1.0  # Default weight

        # Ensure the server URL starts with http:// or https://
        if not server.startswith(('http://', 'https://')):
            server = f"http://{server}"

        backend_servers.append(server)
        weights.append(weight)
        logging.info(f"Added backend server: {server} with weight: {weight}")

    return backend_servers, weights

def query_server_loads(servers):
    """
    Query each server for its current load and return a list of adjusted weights.
    Assumes each server has an endpoint '/load' that returns the load as a JSON object.
    Example response: {"load": 0.5} (where 0.5 means 50% load)
    """
    loads = []
    for server in servers:
        try:
            response = requests.get(f"{server}/load", timeout=2)
            response.raise_for_status()
            load_data = response.json()
            load = load_data.get("load", 1.0)
            loads.append(load)
            logging.info(f"Server {server} reported load: {load}")
        except requests.exceptions.RequestException as e:
            logging.warning(f"Could not retrieve load from {server}: {e}")
            loads.append(1.0)  # Default to maximum load if server is unresponsive
    return loads

def adjust_weights_based_on_load(loads, original_weights):
    """
    Adjust weights based on server loads. Higher load results in lower weight.
    """
    adjusted_weights = []
    for load, original_weight in zip(loads, original_weights):
        adjusted_weight = max(0.01, original_weight / (1 + load))  # Prevent weight from being zero
        adjusted_weights.append(adjusted_weight)
    return adjusted_weights

# Loop until BACKEND_SERVERS is set
BACKEND_SERVERS_ENV = None
while not BACKEND_SERVERS_ENV:
    BACKEND_SERVERS_ENV = get_backend_servers()
    if not BACKEND_SERVERS_ENV:
        logging.info("Waiting for 10 seconds before retrying...")
        time.sleep(10)

# Parse BACKEND_SERVERS with weights
BACKEND_SERVERS, BACKEND_WEIGHTS = parse_backend_servers(BACKEND_SERVERS_ENV)

if not BACKEND_SERVERS:
    logging.error("No valid backend servers found in 'BACKEND_SERVERS' environment variable.")
    raise ValueError("No valid backend servers found in 'BACKEND_SERVERS' environment variable.")

# Check if load sensitivity is enabled
LOAD_SENSITIVE = os.getenv('LOAD_SENSITIVE', 'false').lower() == 'true'

class LoadBalancerHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global BACKEND_WEIGHTS

        if LOAD_SENSITIVE:
            # Query server loads and adjust weights
            loads = query_server_loads(BACKEND_SERVERS)
            BACKEND_WEIGHTS = adjust_weights_based_on_load(loads, BACKEND_WEIGHTS)

        # Select a backend server based on weights
        target_server = random.choices(BACKEND_SERVERS, weights=BACKEND_WEIGHTS, k=1)[0]
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

    def log_message(self, format, *args):
        # Override to prevent default logging; handled by the logging module
        return

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

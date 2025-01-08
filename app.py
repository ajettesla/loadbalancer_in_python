#!/usr/bin/env python3
from flask import Flask, request, jsonify
import socket
import datetime
import psutil  # For monitoring system metrics

app = Flask(__name__)

@app.route('/')
def home():
    # Get 'Hello, World!'
    greeting = 'Hello, World!\n'

    # Get device name (host name)
    device_name = socket.gethostname()
    greeting += f'Device Name: {device_name}\n'

    # Get date and timestamp
    current_datetime = datetime.datetime.now()
    greeting += f'Date and Time: {current_datetime}\n'

    # Get IP address
    # Server's IP address
    try:
        server_ip = socket.gethostbyname(device_name)
    except socket.gaierror:
        server_ip = 'Unable to get IP address'
    greeting += f'Server IP Address: {server_ip}\n'

    # Client's IP address
    client_ip = request.remote_addr
    greeting += f'Client IP Address: {client_ip}\n'

    return greeting

@app.route('/load', methods=['GET'])
def load():
    """
    Returns the current server load as a JSON response.
    The load metric is based on CPU and memory utilization.
    """
    # Get CPU usage as a percentage (scaled to 0.0 - 1.0)
    cpu_usage = psutil.cpu_percent(interval=1) / 100.0

    # Get memory usage as a percentage (scaled to 0.0 - 1.0)
    memory_info = psutil.virtual_memory()
    memory_usage = memory_info.percent / 100.0

    # Combine CPU and memory usage into a single load metric
    # You can customize this formula based on your requirements
    load_metric = (cpu_usage + memory_usage) / 2

    # Return the load metric as JSON
    return jsonify({
        "cpu_usage": cpu_usage,
        "memory_usage": memory_usage,
        "load": load_metric
    })

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)

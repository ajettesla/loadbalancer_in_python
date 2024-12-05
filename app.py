#!/usr/bin/env python3
from flask import Flask, request
import socket
import datetime

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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0',port=80)


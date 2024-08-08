from flask import Flask, jsonify, request
import requests
import datetime
import random

app = Flask(__name__)

SERVICES = ['service1', 'service2', 'service3']
SERVER_URL = 'http://localhost:5000/logs'
API_KEYS = {
    'service1': 'service1-token',
    'service2': 'service2-token',
    'service3': 'service3-token'
}

@app.route('/generate-log', methods=['GET'])
def generate_log():
    service = random.choice(SERVICES)
    log = {
        'timestamp': datetime.datetime.now().isoformat(),
        'serviceName': service,
        'level': random.choice(['info', 'warning', 'error']),
        'message': f'This is a test log message from {service}'
    }
    headers = {'Authorization': API_KEYS[service]}
    
    try:
        response = requests.post(SERVER_URL, json=log, headers=headers)
        return jsonify({'message': 'Log sent', 'log': log}), response.status_code
    except Exception as e:
        return jsonify({'message': 'Failed to send log', 'error': str(e)}), 500

@app.route('/generate-multiple-logs', methods=['POST'])
def generate_multiple_logs():
    count = request.json.get('count', 1)
    logs_sent = []
    
    for _ in range(count):
        service = random.choice(SERVICES)
        log = {
            'timestamp': datetime.datetime.now().isoformat(),
            'serviceName': service,
            'level': random.choice(['info', 'warning', 'error']),
            'message': f'This is a test log message from {service}'
        }
        headers = {'Authorization': API_KEYS[service]}
        
        try:
            response = requests.post(SERVER_URL, json=log, headers=headers)
            logs_sent.append({'log': log, 'status': response.status_code})
        except Exception as e:
            logs_sent.append({'log': log, 'error': str(e)})
    
    return jsonify({'message': f'{len(logs_sent)} logs sent', 'logs': logs_sent})

if __name__ == '__main__':
    app.run(port=5011)
from flask import Flask,  jsonify
import requests
import datetime

app = Flask(__name__)
SERVICE_NAME = 'service2'
SERVER_URL = 'http://localhost:5000/logs'
API_KEY = 'service2-token'


@app.route('/generate-log', methods=['GET'])
def generate_log():
    log = {
        'timestamp': datetime.datetime.now().isoformat(),
        'serviceName': SERVICE_NAME,
        'level': 'info',
        'message': 'This is a test log message from service2'
    }
    headers = {'Authorization': API_KEY}
    try:
        response = requests.post(SERVER_URL, json=log, headers=headers)
        return jsonify({'message': 'Log sent', 'log': log}), response.status_code
    except Exception as e:
        return jsonify({'message': 'Failed to send log', 'error': str(e)}), 500


if __name__ == '__main__':
    app.run(port=5002)

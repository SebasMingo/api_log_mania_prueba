from flask import Flask, request, jsonify
import sqlite3
import datetime

app = Flask(__name__)
DATABASE = 'logging.db'
API_KEYS = ['service1-token', 'service2-token', 'service3-token']


def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL,
                serviceName TEXT NOT NULL,
                level TEXT NOT NULL,
                message TEXT NOT NULL,
                receivedAt TEXT NOT NULL
            )
        ''')
        conn.commit()


@app.route('/logs', methods=['POST'])
def receive_log():
    api_key = request.headers.get('Authorization')
    if api_key not in API_KEYS:
        return jsonify({'message': 'Invalid API key'}), 403

    log_data = request.json
    log_data['receivedAt'] = datetime.datetime.now().isoformat()
    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO logs (timestamp, serviceName, level, message, receivedAt)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                log_data['timestamp'],
                log_data['serviceName'],
                log_data['level'],
                log_data['message'],
                log_data['receivedAt']
            ))
            conn.commit()
        return jsonify({'message': 'Log saved successfully'}), 201
    except Exception as e:
        return jsonify({'message': 'Failed to save log', 'error': str(e)}), 500


@app.route('/logs', methods=['GET'])
def get_logs():
    query = 'SELECT * FROM logs'
    filters = []
    params = []

    start_date = request.args.get('startDate')
    end_date = request.args.get('endDate')
    received_start_date = request.args.get('receivedStartDate')
    received_end_date = request.args.get('receivedEndDate')

    if start_date:
        filters.append('timestamp >= ?')
        params.append(start_date)
    if end_date:
        filters.append('timestamp <= ?')
        params.append(end_date)
    if received_start_date:
        filters.append('receivedAt >= ?')
        params.append(received_start_date)
    if received_end_date:
        filters.append('receivedAt <= ?')
        params.append(received_end_date)

    if filters:
        query += ' WHERE ' + ' AND '.join(filters)
    query += ' ORDER BY timestamp DESC'

    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            logs = [
                {
                    'id': row[0],
                    'timestamp': row[1],
                    'serviceName': row[2],
                    'level': row[3],
                    'message': row[4],
                    'receivedAt': row[5]
                } for row in rows
            ]
        return jsonify(logs)
    except Exception as e:
        return jsonify({'message': 'Failed to fetch logs', 'error': str(e)}), 500


if __name__ == '__main__':
    init_db()
    app.run(port=5010)

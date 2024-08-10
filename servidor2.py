from flask import Flask, request, jsonify  # Importa las clases y funciones necesarias de Flask para construir la API
import sqlite3  # Importa sqlite3 para trabajar con la base de datos SQLite
from datetime import datetime  # Importa datetime para manejar las fechas y horas

app = Flask(__name__)  # Crea una instancia de la aplicación Flask

# Configura la base de datos
def init_db():
    conn = sqlite3.connect('logs.db')  # Conecta con la base de datos SQLite (se crea el archivo si no existe)
    cursor = conn.cursor()  # Crea un cursor para ejecutar comandos SQL
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS logs (  # Crea una tabla llamada logs si no existe
        id INTEGER PRIMARY KEY AUTOINCREMENT,  # Columna id que es la clave primaria y se incrementa automáticamente
        timestamp TEXT,  # Columna para el timestamp del log
        service_name TEXT,  # Columna para el nombre del servicio que genera el log
        severity TEXT,  # Columna para el nivel de severidad del log (INFO, ERROR, DEBUG)
        message TEXT,  # Columna para el mensaje del log
        received_at TEXT  # Columna para el timestamp en que el log fue recibido por el servidor
    )
    ''')
    conn.commit()  # Guarda los cambios en la base de datos
    conn.close()  # Cierra la conexión a la base de datos

init_db()  # Llama a la función para inicializar la base de datos

# Tokens de autenticación para múltiples servicios
VALID_TOKENS = {  # Diccionario con tokens válidos para autenticar servicios
    "service1": "token1",  # Token para el servicio1
    "service2": "token2",  # Token para el servicio2
    "service3": "token3"   # Token para el servicio3
}

def authenticate(token):
    return token in VALID_TOKENS.values()  # Verifica si el token proporcionado está en los tokens válidos

@app.route('/logs', methods=['POST'])  # Define la ruta '/logs' para manejar solicitudes POST
def receive_log():
    token = request.headers.get('Authorization')  # Obtiene el token de autenticación del encabezado de la solicitud
    if not authenticate(token):  # Verifica la autenticación del token
        return jsonify({"error": "Unauthorized"}), 401  # Devuelve un error 401 si la autenticación falla

    log_data = request.json  # Obtiene los datos del log del cuerpo de la solicitud en formato JSON
    timestamp = log_data.get('timestamp')  # Extrae el timestamp del log
    service_name = log_data.get('service_name')  # Extrae el nombre del servicio
    severity = log_data.get('severity')  # Extrae el nivel de severidad del log
    message = log_data.get('message')  # Extrae el mensaje del log
    received_at = datetime.utcnow().isoformat()  # Obtiene la fecha y hora actuales en formato ISO

    conn = sqlite3.connect('logs.db')  # Conecta con la base de datos SQLite
    cursor = conn.cursor()  # Crea un cursor para ejecutar comandos SQL
    cursor.execute('''
    INSERT INTO logs (timestamp, service_name, severity, message, received_at)  # Inserta un nuevo registro en la tabla logs
    VALUES (?, ?, ?, ?, ?)  # Valores a insertar en el registro
    ''', (timestamp, service_name, severity, message, received_at))
    conn.commit()  # Guarda los cambios en la base de datos
    conn.close()  # Cierra la conexión a la base de datos

    return jsonify({"status": "Log received"}), 200  # Devuelve una respuesta JSON confirmando que el log ha sido recibido

@app.route('/logs', methods=['GET'])  # Define la ruta '/logs' para manejar solicitudes GET
def get_logs():
    start_date = request.args.get('start_date')  # Obtiene la fecha de inicio del rango de fechas de los parámetros de la solicitud
    end_date = request.args.get('end_date')  # Obtiene la fecha de fin del rango de fechas de los parámetros de la solicitud
    conn = sqlite3.connect('logs.db')  # Conecta con la base de datos SQLite
    cursor = conn.cursor()  # Crea un cursor para ejecutar comandos SQL
    query = 'SELECT * FROM logs WHERE timestamp BETWEEN ? AND ?'  # Consulta para seleccionar logs dentro del rango de fechas
    cursor.execute(query, (start_date, end_date))  # Ejecuta la consulta con los parámetros proporcionados
    logs = cursor.fetchall()  # Obtiene todos los registros de logs que coinciden con la consulta
    conn.close()  # Cierra la conexión a la base de datos
    return jsonify(logs)  # Devuelve los logs en formato JSON

if __name__ == '__main__':
    app.run(port=5000)  # Ejecuta la aplicación Flask en el puerto 5000

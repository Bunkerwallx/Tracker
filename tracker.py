from flask import Flask, request, render_template_string
import requests
import sqlite3
import datetime

app = Flask(__name__)

# Configuración de la base de datos SQLite
DATABASE = 'ip_logger.db'

def init_db():
    """Inicializa la base de datos."""
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ip TEXT,
            location TEXT,
            browser TEXT,
            timestamp TEXT
        )
    ''')
    conn.commit()
    conn.close()

# Función para guardar datos en la base de datos
def save_to_db(ip, location, browser, timestamp):
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO logs (ip, location, browser, timestamp)
        VALUES (?, ?, ?, ?)
    ''', (ip, location, browser, timestamp))
    conn.commit()
    conn.close()

# Función para obtener datos de geolocalización
def get_geo_info(ip):
    try:
        response = requests.get(f"http://ip-api.com/json/{ip}")
        if response.status_code == 200:
            data = response.json()
            return f"{data.get('city', 'Unknown')}, {data.get('country', 'Unknown')}"
        return "Unknown"
    except Exception:
        return "Unknown"

# Ruta principal
@app.route('/')
def home():
    visitor_ip = request.remote_addr  # Obtiene la IP del visitante
    user_agent = request.headers.get('User-Agent')  # Información del navegador
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Marca de tiempo

    # Geolocalización
    location = get_geo_info(visitor_ip)

    # Guarda los datos en la base de datos
    save_to_db(visitor_ip, location, user_agent, timestamp)

    # Respuesta HTML con mapa (puedes agregar una API key de Google Maps)
    google_maps_iframe = f"""
    <iframe
        width="600"
        height="450"
        style="border:0"
        loading="lazy"
        allowfullscreen
        src="https://www.google.com/maps/embed/v1/place?key=YOUR_GOOGLE_MAPS_API_KEY&q={location.replace(' ', '+')}">
    </iframe>
    """

    return f"""
    <h1>Tu IP ha sido registrada</h1>
    <p><strong>IP:</strong> {visitor_ip}</p>
    <p><strong>Fecha:</strong> {timestamp}</p>
    <p><strong>Ubicación:</strong> {location}</p>
    <p><strong>Navegador:</strong> {user_agent}</p>
    <p>{google_maps_iframe}</p>
    """

# Ruta para visualizar los logs
@app.route('/logs')
def view_logs():
    conn = sqlite3.connect(DATABASE)
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM logs")
    rows = cursor.fetchall()
    conn.close()

    # Generar tabla HTML
    table = "<table border='1'><tr><th>ID</th><th>IP</th><th>Ubicación</th><th>Navegador</th><th>Fecha</th></tr>"
    for row in rows:
        table += f"<tr><td>{row[0]}</td><td>{row[1]}</td><td>{row[2]}</td><td>{row[3]}</td><td>{row[4]}</td></tr>"
    table += "</table>"

    return f"<h1>Registros de IP</h1>{table}"

# Inicia el servidor
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)

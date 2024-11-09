# app.py
from flask import Flask
from flask_socketio import SocketIO
from config import Config
from Model import db
from Controller.usuarioController import usuario_bp
from Controller.ubicacionController import ubicacion_bp
from Controller.OrdenController import orden_bp
from flask_cors import CORS
from socketio_instance import socketio  # Importa la instancia de socketio

app = Flask(__name__)
CORS(app)

app.config.from_object(Config)

# Inicializar socketio con la app Flask
socketio.init_app(app, cors_allowed_origins="*")

# Inicializar la base de datos
db.init_app(app)

# Registrar Blueprints
app.register_blueprint(usuario_bp)
app.register_blueprint(ubicacion_bp)
app.register_blueprint(orden_bp)

@app.before_request
def create_tables():
    db.create_all()

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0', port=5000, allow_unsafe_werkzeug=True)  # socketio.run

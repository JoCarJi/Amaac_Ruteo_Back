from flask import Blueprint, request,jsonify
import requests
import os
from dotenv import load_dotenv
from datetime import datetime
from Model import db
from Model.ubicacion import Ubicacion
from flask_socketio import SocketIO,emit
from socketio_instance import socketio
import requests
from .OrdenController import crearautomatica

ubicacion_bp=Blueprint('ubicacion_bp',__name__)
load_dotenv()

def geocodificar_direccion(direccion):
    api_key = os.getenv('API_KEY_GOOGLE_MAPS')
    url=f'https://maps.googleapis.com/maps/api/geocode/json?address={direccion}&key={api_key}'
    respuesta=requests.get(url)
    data=respuesta.json()

    if data['status']=='OK':
        latitud=data['results'][0]['geometry']['location']['lat']
        longitud=data['results'][0]['geometry']['location']['lng']
        return latitud,longitud
    else:
        return None


def geocode_coordinates(lat, lng):
    api_key = os.getenv('API_KEY_GOOGLE_MAPS')
    url = f'https://maps.googleapis.com/maps/api/geocode/json?latlng={lat},{lng}&key={api_key}'
    response = requests.get(url)
    data = response.json()

    if data['status'] == 'OK':
        return data['results'][0]['formatted_address']
    return None


@ubicacion_bp.route('/guardar-ubicacion', methods=['POST'])
def localizacion():
    data = request.json
    lat = data['latitud']
    lng = data['longitud']
    idUsuario = data['idUsuario']
    botellas = data.get('botellas', 0)
    baldes = data.get('baldes', 0)

    direccion = geocode_coordinates(lat, lng)
    if direccion:
        nueva_ubicacion = Ubicacion(
            idUsuario=idUsuario,
            latitud=lat,
            longitud=lng,
            direccion=direccion,
            fechaHora=datetime.now()
        )
        db.session.add(nueva_ubicacion)
        db.session.commit()

        crearautomatica(nueva_ubicacion.idUbicacion, idUsuario, botellas, baldes)

        socketio.emit('nueva_ubicacion', {'idUsuario': idUsuario, 'latitud': lat, 'longitud': lng})

        return jsonify({'status': 'ubicación guardada', 'direccion': direccion}), 201

    return jsonify({'error': 'No se pudo obtener la dirección'}), 400
# Función para calcular la ruta usando la API de Google Maps Directions
def calcular_ruta(origen, destino):
    api_key = os.getenv('API_KEY_GOOGLE_MAPS')
    url = f'https://maps.googleapis.com/maps/api/directions/json?origin={origen}&destination={destino}&key={api_key}'
    respuesta = requests.get(url)
    data = respuesta.json()

    if data['status'] == 'OK':
        ruta = data['routes'][0]['legs'][0]
        return {
            'distancia': ruta['distance']['text'],
            'duracion': ruta['duration']['text'],
            'pasos': ruta['steps']
        }
    else:
        return None

@ubicacion_bp.route('/calcular-ruta', methods=['POST'])
def calcular_ruta_endpoint():
    data = request.json
    try:
        origen = f"{data['latitud']},{data['longitud']}"
        destino = data['direccion']
    except KeyError as e:
        return jsonify({'error': f'Llave faltante: {str(e)}'}), 400

    ruta = calcular_ruta(origen, destino)
    if ruta:
        return jsonify(ruta), 200
    else:
        return jsonify({'error': 'No se pudo calcular la ruta'}), 400
@socketio.on('conectar_trabajador')
def conectar_trabajador(data):
    emit('respuesta_conexion', {'status': 'Trabajador conectado'}, broadcast=True)
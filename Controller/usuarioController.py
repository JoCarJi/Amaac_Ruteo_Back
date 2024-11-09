from flask import Blueprint, request,jsonify


from Model import db
from Model.usuario import Usuario
from flask_socketio import SocketIO,emit
from socketio_instance import socketio
from sqlalchemy import or_
from werkzeug.security import generate_password_hash,check_password_hash

usuario_bp=Blueprint('usuario_bp',__name__)

@usuario_bp.route('/register', methods=['POST'])
def add_usuario():
    data=request.json
    email = data['email']
    password = data['password']
    nombre=data['nombre']
    apell=data['apell']
    telefono=data['telefono']
    rol=data['rol']

    # Verificar si el usuario ya existe
    if Usuario.query.filter_by(email=email).first():
        emit('register_response', {"message": "Usuario ya registrado"})
        return

    # Crear un nuevo usuario
    hashed_password = generate_password_hash(password)
    new_user = Usuario(
        nombre=nombre,
        apell=apell,
        telefono=telefono,
        email=email,
        password=hashed_password,
        rol=rol
    )
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "Usuario registrado exitosamente"}), 201


@usuario_bp.route('/login', methods=['POST'])
def login():
    data = request.json
    email = data.get('email')
    password = data.get('password')
    user = Usuario.query.filter_by(email=email).first()
    if user and check_password_hash(user.password, password):
        return jsonify({"message": "Inicio de sesión exitoso", "user": {
            "idUsuario": user.idUsuario,
            "nombre": user.nombre,
            "apell": user.apell,
            "telefono": user.telefono,
            "email": user.email,
            "rol": user.rol
        }}), 200
    else:
        return jsonify({"message": "Credenciales incorrectas"}), 401

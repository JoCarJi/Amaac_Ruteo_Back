from flask import Blueprint, request, jsonify
from Model import db
from Model.usuario import Usuario
from Model.ubicacion import Ubicacion
from Model.orden import orden
from socketio_instance import socketio

orden_bp = Blueprint('orden_bp', __name__)

def crearautomatica(idUbicacion, idUsuario, botellas, baldes):
    # Busca el usuario que está creando la orden
    usuario = Usuario.query.filter_by(idUsuario=idUsuario).first()

    if not usuario:
        return {'error': 'El usuario con ID proporcionado no existe'}

    # Crea una nueva orden con los datos proporcionados
    nueva_orden = orden(
        idUbicacion=idUbicacion,
        idUsuario=usuario.idUsuario,  # The user who creates the order
        idWorker=None,  # No worker assigned at creation
        estado='pendiente',
        botellas=botellas,
        baldes=baldes
    )

    # Guarda la nueva orden en la base de datos
    try:
        db.session.add(nueva_orden)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return {'error': f'Error al guardar la orden: {str(e)}'}

    # Emite un evento de nueva orden mediante WebSocket
    socketio.emit('nueva_orden', {
        'idOrden': nueva_orden.idOrden,
        'idUbicacion': idUbicacion,
        'estado': nueva_orden.estado
    })

    return {'mensaje': 'Orden creada correctamente'}


@orden_bp.route('/aceptar-orden/<int:idOrden>', methods=['POST'])
def aceptar_orden(idOrden):
    data = request.json
    trabajador = Usuario.query.filter_by(idUsuario=data['idWorker']).first()

    if not trabajador:
        return jsonify({'error': 'Trabajador no encontrado'}), 404

    Orden = orden.query.filter_by(idOrden=idOrden).first()

    if not Orden:
        return jsonify({'error': 'Orden no encontrada'}), 404

    Orden.idWorker = trabajador.idUsuario  # Assign the worker
    Orden.estado = 'aceptado'

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'Error al actualizar la orden: {str(e)}'}), 500

    socketio.emit('orden_aceptada', {
        'idOrden': Orden.idOrden,
        'idWorker': trabajador.idUsuario,
        'estado': Orden.estado
    })

    return jsonify({'message': 'Orden aceptada', 'idOrden': Orden.idOrden, 'idWorker': trabajador.idUsuario}), 200


@orden_bp.route('/pedidos', methods=['GET'])
def obtener_pedidos():
    pedidos = orden.query.all()
    resultados = []
    for pedido in pedidos:
        ubicacion = Ubicacion.query.get(pedido.idUbicacion)
        usuario = Usuario.query.get(pedido.idUsuario)  # User who created the order
        trabajador = Usuario.query.get(pedido.idWorker)  # Worker who accepted the order (if assigned)

        resultados.append({
            'idOrden': pedido.idOrden,
            'usuario': usuario.nombre,  # User's name who created the order
            'trabajador': trabajador.nombre if trabajador else None,  # Worker’s name (if any)
            'latitud': ubicacion.latitud,
            'longitud': ubicacion.longitud,
            'detalles': 'Detalles del pedido',
            'telefono': usuario.telefono,
            'direccion': ubicacion.direccion
        })

    return jsonify(resultados)

@orden_bp.route('/solicitudes_user/<int:idUser>', methods=['GET'])
def get_pedidos_user(idUser):
    pedidos_user = db.session.query(orden, Ubicacion)\
        .join(Ubicacion, orden.idUbicacion == Ubicacion.idUbicacion)\
        .filter(orden.idUsuario == idUser).all()
    
    resultado = []
    for pedido, ubicacion in pedidos_user:
        resultado.append({
            "direccion": ubicacion.direccion,
            "fecha": ubicacion.fechaHora.strftime('%d/%m/%Y'),
            'botellas': pedido.botellas,
            'baldes': pedido.baldes,
            'estado': pedido.estado
        })

    return jsonify(resultado), 200

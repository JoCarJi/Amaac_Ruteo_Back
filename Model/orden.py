from . import db
from sqlalchemy import Enum


class orden(db.Model):
    __tablename__ = 'orden'
    idOrden = db.Column(db.Integer, primary_key=True)
    idUbicacion = db.Column(db.Integer, db.ForeignKey('ubicacion.idUbicacion'), nullable=False)

    # Foreign key to the user who created the order
    idUsuario = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'), nullable=False)

    # Foreign key to the worker who will handle the order
    idWorker = db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'),
                         nullable=True)  # nullable=True because it may be assigned later

    estado = db.Column(Enum('pendiente', 'cancelado', 'completado', 'aceptado', name='estado_enum'), nullable=False,
                       default='pendiente')
    botellas = db.Column(db.Integer, nullable=False, default=0)
    baldes = db.Column(db.Integer, nullable=False, default=0)

    # Relationships to refer to the Usuario model
    usuario = db.relationship('Usuario', foreign_keys=[idUsuario])
    worker = db.relationship('Usuario', foreign_keys=[idWorker])

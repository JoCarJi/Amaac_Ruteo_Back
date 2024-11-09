from Model import  db

class Ubicacion(db.Model):
    __tablename__= 'ubicacion'
    idUbicacion=db.Column(db.Integer, primary_key=True)
    idUsuario=db.Column(db.Integer, db.ForeignKey('usuario.idUsuario'),nullable=False)
    latitud=db.Column(db.Float,nullable=False)
    longitud=db.Column(db.Float,nullable=False)
    direccion = db.Column(db.String(70), nullable=False)
    fechaHora=db.Column(db.DateTime,nullable=False)



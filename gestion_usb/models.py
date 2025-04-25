
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# Tabla: rol
class Rol(db.Model):
    __tablename__ = 'rol'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    usuarios = db.relationship('Usuario', backref='rol', lazy=True)

# Tabla: cargo
class Cargo(db.Model):
    __tablename__ = 'cargo'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    usuarios = db.relationship('Usuario', backref='cargo', lazy=True)

# Tabla: equipo
class Equipo(db.Model):
    __tablename__ = 'equipo'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    usuarios = db.relationship('Usuario', backref='equipo', lazy=True)

# Tabla: usuario
# Tabla: usuario
class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True)  # ← coincidente con la tabla
    nombre = db.Column(db.String(100), nullable=False)
    correo = db.Column(db.String(100), nullable=False, unique=True)
    contrasena = db.Column(db.String(255), nullable=False)
    id_rol = db.Column(db.Integer, db.ForeignKey('rol.id'), nullable=False)
    id_cargo = db.Column(db.Integer, db.ForeignKey('cargo.id'), nullable=True)
    id_equipo = db.Column(db.Integer, db.ForeignKey('equipo.id'), nullable=True)


# Tabla: apartado
class Apartado(db.Model):
    __tablename__ = 'apartado'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    usuarios = db.relationship('UsuarioApartado', backref='apartado', lazy=True)

# Tabla intermedia usuario_apartado
class UsuarioApartado(db.Model):
    __tablename__ = 'usuario_apartado'
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    id_apartado = db.Column(db.Integer, db.ForeignKey('apartado.id'), nullable=False)

class Proyecto(db.Model):
    __tablename__ = 'proyecto'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text)

    microproyectos = db.relationship('MicroProyecto', back_populates='proyecto')
    seguimientos = db.relationship('Seguimiento', back_populates='proyecto')  # ✅ OK

# models.py

class Seguimiento(db.Model):
    __tablename__ = 'seguimiento'

    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    descripcion = db.Column(db.Text, nullable=False)
    proyecto_id = db.Column(db.Integer, db.ForeignKey('proyecto.id'), nullable=False)

    proyecto = db.relationship('Proyecto', back_populates='seguimientos')




class MicroProyecto(db.Model):
    __tablename__ = 'micro_proyecto'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    id_proyecto = db.Column(db.Integer, db.ForeignKey('proyecto.id', ondelete='CASCADE'))

    proyecto = db.relationship('Proyecto', back_populates='microproyectos')  # ✅ bien

# Tabla: Categoria (para competencias, cursos, etc.)
class Categoria(db.Model):
    __tablename__ = 'categoria'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

    # Relación inversa: una categoría puede tener muchos cursos
    cursos = db.relationship('Cursos', back_populates='categoria', cascade="all, delete", passive_deletes=True)


# Tabla: Cursos
class Cursos(db.Model):
    __tablename__ = 'cursos'

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)

    # Clave foránea hacia Categoria
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id', ondelete='SET NULL'), nullable=True)

    # Relación hacia la tabla Categoria
    categoria = db.relationship('Categoria', back_populates='cursos')

# Tabla: dimension

class Dimension(db.Model):
    __tablename__ = 'dimension'

    id = db.Column('id_dimension', db.Integer, primary_key=True)
    nombre = db.Column('nombre_dimension', db.String(100), nullable=False)
    
    # Relación con preguntas (si las hay en otra tabla como DimensionPregunta)
    preguntas = db.relationship('DimensionPregunta', backref='dimension', lazy=True)

# Tabla: pregunta
class Pregunta(db.Model):
    __tablename__ = 'pregunta'
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(255), nullable=False)
    dimensiones = db.relationship('DimensionPregunta', backref='pregunta', lazy=True)
    respuestas = db.relationship('Respuesta', backref='pregunta', lazy=True)
    

# Tabla intermedia dimension_pregunta
class DimensionPregunta(db.Model):
    __tablename__ = 'dimension_pregunta'
    id = db.Column(db.Integer, primary_key=True)
    id_dimension = db.Column(db.Integer, db.ForeignKey('dimension.id_dimension', ondelete='CASCADE'), nullable=False)
    id_pregunta = db.Column(db.Integer, db.ForeignKey('pregunta.id', ondelete='CASCADE'), nullable=False)

# Tabla: respuesta
class Respuesta(db.Model):
    __tablename__ = 'respuesta'
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(255), nullable=False)
    pregunta_id = db.Column(db.Integer, db.ForeignKey('pregunta.id'), nullable=False)


# Tabla: dimension_respuesta_guardada
class DimensionRespuestaGuardada(db.Model):
    __tablename__ = 'dimension_respuesta_guardada'
    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    id_dimension = db.Column(db.Integer, db.ForeignKey('dimension.id_dimension', ondelete='CASCADE'), nullable=False)
    id_pregunta = db.Column(db.Integer, db.ForeignKey('pregunta.id', ondelete='CASCADE'), nullable=False)
    id_respuesta = db.Column(db.Integer, db.ForeignKey('respuesta.id', ondelete='CASCADE'), nullable=False)

# Tabla: tipo_video
class TipoVideo(db.Model):
    __tablename__ = 'tipo_video'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

# Tabla: video
class Video(db.Model):
    __tablename__ = 'video'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    tipo_id = db.Column(db.Integer, db.ForeignKey('tipo_video.id', ondelete='SET NULL'))

    tipo_rel = db.relationship('TipoVideo', backref='videos')


# Tabla: podcast
class Podcast(db.Model):
    __tablename__ = 'podcast'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    tipo = db.Column(db.String(100), nullable=True)

# Tabla: historial_version
class HistorialVersion(db.Model):
    __tablename__ = 'historial_version'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    version = db.Column(db.String(10), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    autor = db.Column(db.String(100), nullable=False)
    revisor = db.Column(db.String(100), nullable=False)

# Tabla: seccion
class Seccion(db.Model):
    __tablename__ = 'seccion'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

# Tabla: indicador
class Indicador(db.Model):
    __tablename__ = 'indicador'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    seccion_id = db.Column(db.Integer, db.ForeignKey('seccion.id', ondelete='CASCADE'), nullable=True)

# Tabla: evaluacion
class Evaluacion(db.Model):
    __tablename__ = 'evaluacion'
    id = db.Column(db.Integer, primary_key=True)
    fecha = db.Column(db.Date, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    evaluador_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)

# Tabla: resultado_evaluacion
class ResultadoEvaluacion(db.Model):
    __tablename__ = 'resultado_evaluacion'
    id = db.Column(db.Integer, primary_key=True)
    evaluacion_id = db.Column(db.Integer, db.ForeignKey('evaluacion.id', ondelete='CASCADE'), nullable=False)
    indicador_id = db.Column(db.Integer, db.ForeignKey('indicador.id', ondelete='CASCADE'), nullable=False)
    valor = db.Column(db.Float, nullable=False)

# Tabla: reporte
class Reporte(db.Model):
    __tablename__ = 'reporte'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)
    fecha_generacion = db.Column(db.DateTime, nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)

# Tabla: log_acceso
class LogAcceso(db.Model):
    __tablename__ = 'log_acceso'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    fecha_hora = db.Column(db.DateTime, nullable=False)
    accion = db.Column(db.String(255), nullable=False)

# Tabla: certificado
class Certificado(db.Model):
    __tablename__ = 'certificado'
    id = db.Column(db.Integer, primary_key=True)
    
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id', ondelete='CASCADE'), nullable=False)
    
    fecha_emision = db.Column(db.Date, nullable=False)
    
    # Relaciones para acceder a los datos
    usuario = db.relationship("Usuario", backref=db.backref("certificados", lazy=True))
    curso = db.relationship("Cursos", backref=db.backref("certificados", lazy=True))


# Tabla: comentario
class Comentario(db.Model):
    __tablename__ = 'comentario'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    contenido = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)

# Tabla: notificacion
class Notificacion(db.Model):
    __tablename__ = 'notificacion'
    id = db.Column(db.Integer, primary_key=True)
    mensaje = db.Column(db.String(255), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    leida = db.Column(db.Boolean, default=False)

# Tabla: configuracion_usuario
class ConfiguracionUsuario(db.Model):
    __tablename__ = 'configuracion_usuario'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    tema = db.Column(db.String(50), default='claro')
    idioma = db.Column(db.String(50), default='es')

# Tabla: recurso
class Recurso(db.Model):
    __tablename__ = 'recurso'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    url = db.Column(db.String(255), nullable=False)

# Tabla: tipo_recurso
class TipoRecurso(db.Model):
    __tablename__ = 'tipo_recurso'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)

# Tabla: archivo_adjunto
class ArchivoAdjunto(db.Model):
    __tablename__ = 'archivo_adjunto'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(255), nullable=False)
    url = db.Column(db.String(255), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)

# Tabla: encuesta
class Encuesta(db.Model):
    __tablename__ = 'encuesta'
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(100), nullable=False)
    descripcion = db.Column(db.Text, nullable=True)

# Tabla: pregunta_encuesta
class PreguntaEncuesta(db.Model):
    __tablename__ = 'pregunta_encuesta'
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(255), nullable=False)
    encuesta_id = db.Column(db.Integer, db.ForeignKey('encuesta.id', ondelete='CASCADE'), nullable=False)

# Tabla: respuesta_encuesta
class RespuestaEncuesta(db.Model):
    __tablename__ = 'respuesta_encuesta'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    pregunta_id = db.Column(db.Integer, db.ForeignKey('pregunta_encuesta.id', ondelete='CASCADE'), nullable=False)
    respuesta = db.Column(db.Text, nullable=False)

# Tabla: inscripcion_curso
class InscripcionCurso(db.Model):
    __tablename__ = 'inscripcion_curso'
    id = db.Column(db.Integer, primary_key=True)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id', ondelete='CASCADE'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    fecha_inscripcion = db.Column(db.Date, nullable=False)

# Tabla: favorito_video
class FavoritoVideo(db.Model):
    __tablename__ = 'favorito_video'
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id', ondelete='CASCADE'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)

# Tabla: progreso_usuario
class ProgresoUsuario(db.Model):
    __tablename__ = 'progreso_usuario'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    curso_id = db.Column(db.Integer, db.ForeignKey('cursos.id', ondelete='CASCADE'), nullable=False)
    porcentaje = db.Column(db.Float, nullable=False)

# Tabla: feedback
class Feedback(db.Model):
    __tablename__ = 'feedback'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    mensaje = db.Column(db.Text, nullable=False)
    fecha = db.Column(db.DateTime, nullable=False)

# Tabla: sesion
class Sesion(db.Model):
    __tablename__ = 'sesion'
    id = db.Column(db.Integer, primary_key=True)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    inicio = db.Column(db.DateTime, nullable=False)
    fin = db.Column(db.DateTime, nullable=True)

# Tabla: progreso_video
class ProgresoVideo(db.Model):
    __tablename__ = 'progreso_video'
    id = db.Column(db.Integer, primary_key=True)
    video_id = db.Column(db.Integer, db.ForeignKey('video.id', ondelete='CASCADE'), nullable=False)
    usuario_id = db.Column(db.Integer, db.ForeignKey('usuario.id', ondelete='CASCADE'), nullable=False)
    segundos_vistos = db.Column(db.Integer, nullable=False)

# Tabla: dimension_respuesta
class DimensionRespuesta(db.Model):
    __tablename__ = 'dimension_respuesta'
    id = db.Column(db.Integer, primary_key=True)
    texto = db.Column(db.String(255), nullable=False)
    nivel = db.Column(db.Integer, nullable=False)

from datetime import date
from gestion_usb.models import db

class RespuestaDimension(db.Model):
    __tablename__ = 'respuesta_dimension'

    id = db.Column(db.Integer, primary_key=True)
    id_usuario = db.Column(db.Integer, db.ForeignKey('usuario.id'), nullable=False)
    id_dimension = db.Column(db.Integer, db.ForeignKey('dimension.id_dimension'), nullable=False)  # 👈 corregido
    id_pregunta = db.Column(db.Integer, db.ForeignKey('pregunta.id'), nullable=False)              # 👈 corregido
    id_respuesta = db.Column(db.Integer, db.ForeignKey('respuesta.id'), nullable=False)
    fecha_respuesta = db.Column(db.Date, nullable=False, default=date.today)

    usuario = db.relationship("Usuario", backref="respuestas_dimension")
    dimension = db.relationship("Dimension", backref="respuestas_dimension", foreign_keys=[id_dimension])
    pregunta = db.relationship("Pregunta", backref="respuestas_dimension", foreign_keys=[id_pregunta])
    respuesta = db.relationship("Respuesta", backref="respuestas_dimension")


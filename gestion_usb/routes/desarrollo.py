from flask import Blueprint, render_template, request, redirect, url_for, session
from datetime import date

from gestion_usb.models import (
    db, Usuario, Cursos, Categoria, InscripcionCurso, Certificado,
    Video, TipoVideo, FavoritoVideo, ProgresoVideo, Podcast, ProgresoUsuario
)

desarrollo_bp = Blueprint('desarrollo_bp', __name__, url_prefix='/desarrollo')


# ========================================================
# VISTA PRINCIPAL DEL MÓDULO DE DESARROLLO
# ========================================================

@desarrollo_bp.route('/')
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('usuarios_bp.login'))
    usuario = Usuario.query.get(session['usuario_id'])
    return render_template('desarrollo.html', usuario=usuario)


# ========================================================
# CURSOS DISPONIBLES Y PROGRESO
# ========================================================

@desarrollo_bp.route('/cursos')
def cursos():
    cursos = Cursos.query.all()
    usuario_id = session.get('usuario_id')

    progreso = {
        p.curso_id: p.porcentaje
        for p in ProgresoUsuario.query.filter_by(usuario_id=usuario_id).all()
    }

    return render_template('cursos.html', cursos=cursos, progreso=progreso)


# ========================================================
# INSCRIPCIÓN A CURSOS
# ========================================================

@desarrollo_bp.route('/cursos/inscribirse/<int:curso_id>', methods=['POST'])
def inscribirse_curso(curso_id):
    usuario_id = session.get('usuario_id')
    if not usuario_id:
        return redirect(url_for('usuarios_bp.login'))

    ya_inscrito = InscripcionCurso.query.filter_by(curso_id=curso_id, usuario_id=usuario_id).first()
    if not ya_inscrito:
        inscripcion = InscripcionCurso(
            curso_id=curso_id,
            usuario_id=usuario_id,
            fecha_inscripcion=date.today()
        )
        db.session.add(inscripcion)
        db.session.commit()
    return redirect(url_for('desarrollo_bp.cursos'))


# ========================================================
# CERTIFICADOS OBTENIDOS
# ========================================================

@desarrollo_bp.route('/certificados')
def certificados():
    usuario_id = session.get('usuario_id')
    lista = Certificado.query.filter_by(usuario_id=usuario_id).all()
    return render_template('certificados.html', certificados=lista)


# ========================================================
# VIDEOS Y PROGRESO
# ========================================================

@desarrollo_bp.route('/videos')
def videos():
    lista = Video.query.all()
    usuario_id = session.get('usuario_id')
    favoritos = {f.video_id for f in FavoritoVideo.query.filter_by(usuario_id=usuario_id).all()}
    return render_template('videos.html', videos=lista, favoritos=favoritos)


@desarrollo_bp.route('/videos/favorito/<int:video_id>', methods=['POST'])
def marcar_favorito(video_id):
    usuario_id = session.get('usuario_id')
    ya_fav = FavoritoVideo.query.filter_by(video_id=video_id, usuario_id=usuario_id).first()
    if not ya_fav:
        nuevo = FavoritoVideo(video_id=video_id, usuario_id=usuario_id)
        db.session.add(nuevo)
        db.session.commit()
    return redirect(url_for('desarrollo_bp.videos'))


@desarrollo_bp.route('/videos/progreso/<int:video_id>', methods=['POST'])
def registrar_progreso(video_id):
    usuario_id = session.get('usuario_id')
    segundos = int(request.form['segundos'])

    progreso = ProgresoVideo.query.filter_by(video_id=video_id, usuario_id=usuario_id).first()
    if progreso:
        progreso.segundos_vistos = max(progreso.segundos_vistos, segundos)
    else:
        progreso = ProgresoVideo(video_id=video_id, usuario_id=usuario_id, segundos_vistos=segundos)
        db.session.add(progreso)

    db.session.commit()
    return redirect(url_for('desarrollo_bp.videos'))


# ========================================================
# PODCASTS EDUCATIVOS
# ========================================================

@desarrollo_bp.route('/podcasts')
def podcasts():
    lista = Podcast.query.all()
    return render_template('podcasts.html', podcasts=lista)

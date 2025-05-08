from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from gestion_usb.models import (
    db, Usuario, MicroProyecto, Proyecto, Dimension, DimensionPregunta,
    Respuesta, DimensionRespuestaGuardada, Rol, Cargo, Equipo, NivelContribucion, Categoria, RespuestaDimension, Pregunta
)


desempeno_bp = Blueprint('desempeno_bp', __name__, url_prefix='/desempeno')

@desempeno_bp.route('/')
def index():
    if 'usuario_id' not in session:
        return redirect(url_for('usuarios_bp.login'))
    usuario = Usuario.query.get(session['usuario_id'])
    return render_template('desempeno.html', usuario=usuario)

@desempeno_bp.route('/microproyectos')
def microproyectos():
    if 'usuario_id' not in session:
        return redirect(url_for('usuarios_bp.login'))
    usuario = Usuario.query.get(session['usuario_id'])
    lista = MicroProyecto.query.all()
    return render_template('microproyectos.html', microproyectos=lista, usuario=usuario)

@desempeno_bp.route('/evaluar', methods=['GET', 'POST'])
def evaluar_dimensiones():
    dimensiones = Dimension.query.all()
    respuestas = Respuesta.query.all()  # ← corregido

    if request.method == 'POST':
        usuario_id = session.get('usuario_id')
        for dimension in dimensiones:
            for pregunta in dimension.preguntas:
                id_pregunta = pregunta.id
                id_respuesta = request.form.get(f"respuesta_{id_pregunta}")
                if id_respuesta:
                    respuesta_guardada = DimensionRespuestaGuardada(
                        id_usuario=usuario_id,
                        id_pregunta=id_pregunta,
                        id_respuesta=id_respuesta
                    )
                    db.session.add(respuesta_guardada)
        db.session.commit()
        flash("Evaluación guardada exitosamente", "success")
        return redirect(url_for('desempeno_bp.index'))

    return render_template('evaluar_dimensiones.html', dimensiones=dimensiones, respuestas=respuestas)

@desempeno_bp.route('/dashboard')
def dashboard_desempeno():
    total = DimensionPregunta.query.count()
    completadas = DimensionRespuestaGuardada.query.distinct(DimensionRespuestaGuardada.id_pregunta).count()
    pendientes = total - completadas
    promedio = 0

    if total > 0:
        total_valores = (
            db.session.query(db.func.avg(Respuesta.id))
            .join(Respuesta, Respuesta.id == DimensionRespuestaGuardada.id_respuesta)
            .scalar()
        )
        promedio = round(total_valores or 0, 1)


    indicadores = {
        'completadas': completadas,
        'pendientes': pendientes,
        'promedio': promedio
    }

    return render_template('dashboard_desempeno.html', indicadores=indicadores)

@desempeno_bp.route('/contribuciones')
def contribuciones_individuales():
    if 'usuario_id' not in session:
        return redirect(url_for('usuarios_bp.login'))

    usuario = Usuario.query.get(session['usuario_id'])

    # Lógica para filtrar los usuarios según su rol
    if usuario.rol.nombre == 'Administrador':
        usuarios = Usuario.query.join(Equipo).filter(Equipo.id == usuario.id_equipo).all()  # Los administradores ven todos los usuarios de su equipo
    
    elif usuario.rol.nombre == 'Docente':
        usuarios = Usuario.query.join(Equipo).filter(Equipo.id == usuario.id_equipo).all()  # Docentes ven a los estudiantes de su equipo
    
    elif usuario.rol.nombre == 'Líder':
        usuarios = Usuario.query.join(Equipo).filter(Equipo.id == usuario.id_equipo).all()  # Líderes ven a los miembros de su equipo
    
    elif usuario.rol.nombre == 'Estudiante':
        usuarios = Usuario.query.filter(Usuario.id_equipo == usuario.id_equipo).all()  # Estudiantes ven solo a los miembros de su equipo
    
    elif usuario.rol.nombre == 'Colaborador':
        usuarios = Usuario.query.join(Equipo).filter(Equipo.id == usuario.id_equipo).all()  # Colaboradores también ven a su equipo

    else:
        usuarios = []  # Si el rol no es reconocido, no muestra usuarios

    # Obtener roles, cargos, equipos y niveles de contribución para el formulario
    roles = Rol.query.all()
    cargos = Cargo.query.all()
    equipos = Equipo.query.all()
    niveles_contribucion = NivelContribucion.query.all()  # Traemos los niveles de contribución

    return render_template(
        'contribuciones_individuales.html',
        usuario=usuario,
        usuarios=usuarios,
        roles=roles,
        cargos=cargos,
        equipos=equipos,
        niveles_contribucion=niveles_contribucion  # Pasamos los niveles de contribución a la plantilla
    )


@desempeno_bp.route('/contribuciones/<int:usuario_id>')
def detalle_colaborador(usuario_id):
    if 'usuario_id' not in session:
        return redirect(url_for('usuarios_bp.login'))

    colaborador = Usuario.query \
        .outerjoin(Cargo).outerjoin(Equipo).outerjoin(Rol) \
        .filter(Usuario.id == usuario_id).first()

    if not colaborador:
        flash("Colaborador no encontrado", "danger")
        return redirect(url_for('desempeno_bp.contribuciones_individuales'))

    categorias = [
        {"id": 1, "nombre": "Competencias Transversales", "icono": "icono_transversales.png"},
        {"id": 2, "nombre": "Competencias Docentes", "icono": "icono_docentes.png"},
        {"id": 3, "nombre": "Concentración de Propósitos", "icono": "icono_propositos.png"},
        {"id": 4, "nombre": "Factores Clave del Éxito", "icono": "icono_exito.png"},
        {"id": 5, "nombre": "Seguimiento a Proyectos", "icono": "icono_proyectos.png"},
        {"id": 6, "nombre": "Resultados", "icono": "icono_resultados.png"}
    ]

    return render_template(
        'detalle_colaborador.html',
        usuario=Usuario.query.get(session['usuario_id']),
        colaborador=colaborador,
        categorias=categorias
    )

@desempeno_bp.route('/agregar-miembro', methods=['POST'])
def agregar_miembro():
    nombre = request.form['nombre']
    correo = request.form['correo']
    contrasena = request.form['contrasena']
    id_rol = request.form.get('id_rol') or 3
    id_cargo = request.form.get('id_cargo') or None
    id_equipo = request.form.get('id_equipo') or None

    nuevo = Usuario(
        nombre=nombre,
        correo=correo,
        contrasena=contrasena,
        id_rol=id_rol,
        id_cargo=id_cargo,
        id_equipo=id_equipo
    )
    db.session.add(nuevo)
    db.session.commit()
    flash("Miembro agregado correctamente", "success")
    return redirect(url_for('desempeno_bp.contribuciones_individuales'))

@desempeno_bp.route('/contribuciones/<int:usuario_id>/transversales', methods=['GET', 'POST'])
def evaluar_transversales(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    preguntas = DimensionPregunta.query.filter_by(id_dimension=1).all()
    respuestas = Respuesta.query.all()  # ← corregido

    if request.method == 'POST':
        for pregunta in preguntas:
            id_respuesta = request.form.get(f"respuesta_{pregunta.id}")
            if id_respuesta:
                respuesta_guardada = DimensionRespuestaGuardada(
                    id_usuario=usuario_id,
                    id_pregunta=pregunta.id,
                    id_respuesta=id_respuesta
                )
                db.session.add(respuesta_guardada)
        db.session.commit()
        flash("Respuestas guardadas correctamente", "success")
        return redirect(url_for('desempeno_bp.contribuciones_individuales'))

    return render_template('formularios/transversales.html', usuario=usuario, preguntas=preguntas, respuestas=respuestas)

@desempeno_bp.route('/colaborador/<int:usuario_id>/categoria/<int:categoria_id>', methods=['GET', 'POST'])
def formulario_categoria(usuario_id, categoria_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    categoria = Categoria.query.get_or_404(categoria_id)
    preguntas = DimensionPregunta.query.filter_by(id_dimension=categoria_id).all()
    respuestas = Respuesta.query.all()  # ← corregido

    if request.method == 'POST':
        for pregunta in preguntas:
            respuesta_id = request.form.get(f'respuesta_{pregunta.id}')
            if respuesta_id:
                guardado = DimensionRespuestaGuardada(
                    id_usuario=usuario_id,
                    id_pregunta=pregunta.id,
                    id_respuesta=respuesta_id,
                    id_dimension=categoria_id
                )
                db.session.add(guardado)
        db.session.commit()
        flash('Respuestas guardadas correctamente', 'success')
        return redirect(url_for('desempeno_bp.contribuciones_individuales'))

    return render_template(
        'formulario_categoria.html',
        usuario=usuario,
        categoria=categoria,
        preguntas=preguntas,
        respuestas=respuestas
    )
@desempeno_bp.route('/colaborador/<int:usuario_id>/origen/<string:origen>', methods=['GET', 'POST'])
def formulario_por_origen(usuario_id, origen):
    print(f"📢 Entrando a formulario_por_origen con usuario_id={usuario_id}, origen={origen}")

    # Validar origen existente en la tabla pregunta
    origenes_validos = db.session.query(Pregunta.origen).distinct().all()
    origenes_validos = [o[0] for o in origenes_validos]

    if origen not in origenes_validos:
        flash(f"Origen '{origen}' no válido o no registrado en la base de datos.", "danger")
        return redirect(url_for('desempeno_bp.contribuciones_individuales'))

    # Obtener usuario
    usuario = Usuario.query.get_or_404(usuario_id)

    # Obtener preguntas del origen solicitado
    preguntas_raw = Pregunta.query.filter_by(origen=origen).all()

    # Asociar respuestas a cada pregunta
    preguntas = []
    for pregunta in preguntas_raw:
        pregunta.respuestas = Respuesta.query.filter_by(pregunta_id=pregunta.id).all()
        preguntas.append(pregunta)

    # Procesar formulario
    if request.method == 'POST':
        for pregunta in preguntas:
            respuesta_id = request.form.get(f'respuesta_{pregunta.id}')
            if respuesta_id:
                nueva_respuesta = DimensionRespuestaGuardada(
                    id_usuario=usuario_id,
                    id_pregunta=pregunta.id,
                    id_respuesta=int(respuesta_id),
                    id_dimension=None
                )
                db.session.add(nueva_respuesta)

        db.session.commit()
        flash('Respuestas guardadas correctamente', 'success')
        return redirect(url_for('desempeno_bp.contribuciones_individuales'))

    return render_template(
        'formulario_categoria.html',
        usuario=usuario,
        origen=origen,
        preguntas=preguntas
    )


@desempeno_bp.route('/colaborador/<int:usuario_id>', methods=['GET'])
def formulario_dimension_directo(usuario_id):
    return redirect(url_for(
        'desempeno_bp.formulario_por_origen',
        usuario_id=usuario_id,
        origen='dimension_pregunta'
    ))


@desempeno_bp.route('/propositos/estrategico')
def proposito_estrategico():
    if 'usuario_id' not in session:
        return redirect(url_for('usuarios_bp.login'))

    usuario = Usuario.query.get(session['usuario_id'])
    proyectos = Proyecto.query.all()

    return render_template(
        'Propositos/proposito_estrategico.html',
        usuario=usuario,
        proyectos=proyectos
    )


@desempeno_bp.route('/propositos/mejora')
def proposito_mejora():
    usuario = Usuario.query.get(session['usuario_id'])
    return render_template('Propositos/proposito_mejora.html', usuario=usuario)

@desempeno_bp.route('/propositos/disponibilidad')
def proposito_disponibilidad():
    usuario = Usuario.query.get(session['usuario_id'])
    return render_template('Propositos/proposito_disponibilidad.html', usuario=usuario)



from datetime import date
from gestion_usb.models import db, Usuario, Proyecto, Seguimiento

# Vista principal para la concertación de propósitos
@desempeno_bp.route('/concentracion')
def concentracion_propositos():
    if 'usuario_id' not in session:
        return redirect(url_for('usuarios_bp.login'))

    usuario = Usuario.query.get(session['usuario_id'])
    proyectos = Proyecto.query.all()  # ← obligatorio para acceder al ID

    tarjetas = [
        {
            "titulo": "Concertación de Propósitos Estratégicos",
            "descripcion": "Impulsa el cumplimiento institucional alineando esfuerzos con la misión y visión.",
            "enlace": url_for('desempeno_bp.proposito_estrategico')
        },
        {
            "titulo": "Concertación de Propósitos Personales",
            "descripcion": "Fortalece el desarrollo individual dentro del marco institucional.",
            "enlace": url_for('desempeno_bp.proposito_personal', proyecto_id=proyectos[0].id) if proyectos else "#"
        },
        {
            "titulo": "Concertación de Propósitos para la Mejora de Procesos",
            "descripcion": "Alinea la mejora continua con los objetivos estratégicos de la institución.",
            "enlace": url_for('desempeno_bp.proposito_mejora')
        },
        {
            "titulo": "Concertación de Disponibilidad",
            "descripcion": "Asegura la planificación efectiva del tiempo y recursos del equipo.",
            "enlace": url_for('desempeno_bp.proposito_disponibilidad')
        },
    ]

    return render_template(
        'concentracion_propositos.html',
        tarjetas=tarjetas,
        usuario=usuario
    )


# Ruta para propósitos personales con seguimiento
@desempeno_bp.route('/propositos/personal/<int:proyecto_id>', methods=['GET', 'POST'])
def proposito_personal(proyecto_id):
    if 'usuario_id' not in session:
        return redirect(url_for('usuarios_bp.login'))

    usuario = Usuario.query.get(session['usuario_id'])
    proyecto = Proyecto.query.get_or_404(proyecto_id)

    if request.method == 'POST':
        descripcion = request.form['descripcion']
        fecha = request.form.get('fecha', date.today())
        
        nuevo_seguimiento = Seguimiento(
            descripcion=descripcion,
            fecha=fecha,
            proyecto_id=proyecto.id
        )
        db.session.add(nuevo_seguimiento)
        db.session.commit()
        return redirect(url_for('desempeno_bp.proposito_personal', proyecto_id=proyecto.id))

    seguimientos = Seguimiento.query.filter_by(proyecto_id=proyecto.id).all()

    return render_template(
        'Propositos/proposito_personal.html',
        usuario=usuario,
        proyecto=proyecto,
        seguimientos=seguimientos,
        fecha_actual=date.today().strftime('%Y-%m-%d')
    )

@desempeno_bp.route('/otras_contribuciones')
def otras_contribuciones():
    usuario = session.get('usuario')
    return render_template('otras_contribuciones.html', usuario=usuario)

@desempeno_bp.route('/analisis_organizacional')
def analisis_organizacional():
    if 'usuario_id' not in session:
        return redirect(url_for('usuarios_bp.login'))

    usuario = Usuario.query.get(session['usuario_id'])
    dimensiones = Dimension.query.all()

    return render_template(
        'analisis_organizacional.html',
        usuario=usuario,
        dimensiones=dimensiones
    )



##################################################
@desempeno_bp.route('/colaborador/<int:usuario_id>/dimension/<int:dimension_id>', methods=['GET', 'POST'])
def formulario_dimension(usuario_id, dimension_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    dimension = Dimension.query.get_or_404(dimension_id)

    # usa otro nombre para evitar conflicto con el modelo
    preguntas_raw = db.session.query(DimensionPregunta).filter_by(id_dimension=dimension_id).all()

    for dp in preguntas_raw:
        dp.pregunta = Pregunta.query.get(dp.id_pregunta)
        dp.pregunta.respuestas = Respuesta.query.filter_by(pregunta_id=dp.pregunta.id).all()

    if request.method == 'POST':
        for dp in preguntas_raw:
            respuesta_id = request.form.get(f'respuesta_{dp.pregunta.id}')
            if respuesta_id:
                guardado = RespuestaDimension(
                    id_usuario=usuario.id,
                    id_dimension=dimension.id,
                    id_pregunta=dp.pregunta.id,
                    id_respuesta=int(respuesta_id),
                    fecha_respuesta=date.today()
                )
                db.session.add(guardado)
        db.session.commit()
        flash('Respuestas guardadas correctamente', 'success')
        return redirect(url_for('desempeno_bp.analisis_organizacional'))

    return render_template(
        'formulario_dimension.html',
        usuario=usuario,
        dimension=dimension,
        preguntas=preguntas_raw
    )

#####################################################
@desempeno_bp.route('/propositos/estrategico/<int:proyecto_id>')
def detalle_proyecto_estrategico(proyecto_id):
    if 'usuario_id' not in session:
        return redirect(url_for('usuarios_bp.login'))

    usuario = Usuario.query.get(session['usuario_id'])  # ✅ Este es el que faltaba
    proyecto = Proyecto.query.get_or_404(proyecto_id)
    microproyectos = proyecto.microproyectos

    return render_template(
        'Propositos/detalle_proyecto.html',
        usuario=usuario,
        proyecto=proyecto,
        microproyectos=microproyectos
    )

@desempeno_bp.route('/preguntas_usuario/<int:usuario_id>')
def preguntas_por_usuario(usuario_id):
    usuario = Usuario.query.get_or_404(usuario_id)
    preguntas = Pregunta.query.filter_by(nivel_contribucion_id=usuario.nivel_contribucion_id).all()

    return render_template('preguntas_por_usuario.html', usuario=usuario, preguntas=preguntas)



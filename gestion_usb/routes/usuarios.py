from flask import Blueprint, render_template, request, redirect, url_for, session
from gestion_usb.models import db, Usuario, Rol, Cargo, Equipo, NivelContribucion

usuarios_bp = Blueprint('usuarios_bp', __name__)


# ========================================================
#                    RUTAS PRINCIPALES
# ========================================================

@usuarios_bp.route('/')
def inicio():
    return redirect(url_for('presentacion_bp.ver_presentacion'))


@usuarios_bp.route('/dashboard')
def dashboard():
    if 'usuario_id' not in session:
        return redirect(url_for('usuarios_bp.login'))
    usuario = Usuario.query.get(session['usuario_id'])
    return render_template('dashboard.html', usuario=usuario)



@usuarios_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('usuarios_bp.login'))


# ========================================================
#                    AUTENTICACIÓN
# ========================================================

@usuarios_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        correo = request.form['correo']
        contrasena = request.form['contrasena']
        usuario = Usuario.query.filter_by(correo=correo, contrasena=contrasena).first()
        if usuario:
            session['usuario_id'] = usuario.id
            return redirect(url_for('usuarios_bp.dashboard'))
        else:
            return render_template('login.html', error="Credenciales incorrectas")
    return render_template('login.html')


# ========================================================
#                   GESTIÓN DE USUARIOS
# ========================================================

@usuarios_bp.route('/usuarios')
def lista_usuarios():
    if 'usuario_id' not in session:
        return redirect(url_for('usuarios_bp.login'))
    
    usuario_actual = Usuario.query.get(session['usuario_id'])
    rol_actual = usuario_actual.rol.nombre  # Suponiendo que el modelo Rol tiene un campo 'nombre'
    
    # Filtrar los usuarios según el rol del usuario actual
    if rol_actual == 'Administrador':
        # El Administrador puede ver todos los usuarios
        usuarios = Usuario.query \
            .join(Rol, Usuario.id_rol == Rol.id) \
            .outerjoin(Cargo, Usuario.id_cargo == Cargo.id) \
            .outerjoin(Equipo, Usuario.id_equipo == Equipo.id) \
            .outerjoin(NivelContribucion, Usuario.nivel_contribucion_id == NivelContribucion.id_nivel) \
            .add_entity(Rol).add_entity(Cargo).add_entity(Equipo).add_entity(NivelContribucion).all()
    
    elif rol_actual == 'Docente' or rol_actual == 'Líder':
        # Docentes y Líderes solo ven los estudiantes que están en su equipo
        usuarios = Usuario.query \
            .join(Rol, Usuario.id_rol == Rol.id) \
            .outerjoin(Cargo, Usuario.id_cargo == Cargo.id) \
            .outerjoin(Equipo, Usuario.id_equipo == Equipo.id) \
            .outerjoin(NivelContribucion, Usuario.nivel_contribucion_id == NivelContribucion.id_nivel) \
            .filter(Equipo.id == usuario_actual.id_equipo) \
            .add_entity(Rol).add_entity(Cargo).add_entity(Equipo).add_entity(NivelContribucion).all()
    
    elif rol_actual == 'Estudiante':
        # Los estudiantes solo ven a su docente, líder, colaborador o estudiante dentro de su equipo
        usuarios = Usuario.query \
            .join(Rol, Usuario.id_rol == Rol.id) \
            .outerjoin(Cargo, Usuario.id_cargo == Cargo.id) \
            .outerjoin(Equipo, Usuario.id_equipo == Equipo.id) \
            .outerjoin(NivelContribucion, Usuario.nivel_contribucion_id == NivelContribucion.id_nivel) \
            .filter(Equipo.id == usuario_actual.id_equipo) \
            .filter(Rol.nombre.in_(['Docente', 'Líder', 'Colaborador', 'Estudiante'])) \
            .add_entity(Rol).add_entity(Cargo).add_entity(Equipo).add_entity(NivelContribucion).all()
    
    elif rol_actual == 'Colaborador':
        # Los colaboradores tienen los mismos privilegios que los líderes (pueden ver su equipo)
        usuarios = Usuario.query \
            .join(Rol, Usuario.id_rol == Rol.id) \
            .outerjoin(Cargo, Usuario.id_cargo == Cargo.id) \
            .outerjoin(Equipo, Usuario.id_equipo == Equipo.id) \
            .outerjoin(NivelContribucion, Usuario.nivel_contribucion_id == NivelContribucion.id_nivel) \
            .filter(Equipo.id == usuario_actual.id_equipo) \
            .add_entity(Rol).add_entity(Cargo).add_entity(Equipo).add_entity(NivelContribucion).all()

    # Crear una lista de usuarios con las relaciones cargadas
    usuarios_con_relaciones = []
    for usuario, rol, cargo, equipo, nivel_contribucion in usuarios:
        usuario.rol = rol
        usuario.cargo = cargo
        usuario.equipo = equipo
        usuario.nivel_contribucion = nivel_contribucion
        usuarios_con_relaciones.append(usuario)
    
    return render_template('usuarios.html', usuarios=usuarios_con_relaciones)




# Rutas de gestión de usuarios

@usuarios_bp.route('/usuarios/crear', methods=['GET', 'POST'])
def crear_usuario():
    if 'usuario_id' not in session:
        return redirect(url_for('usuarios_bp.login'))
    
    usuario_actual = Usuario.query.get(session['usuario_id'])
    rol_actual = usuario_actual.rol.nombre  # Suponiendo que el modelo Rol tiene un campo 'nombre'

    if rol_actual not in ['Administrador', 'Docente', 'Líder', 'Colaborador']:
        return redirect(url_for('usuarios_bp.dashboard'))
    
    roles = Rol.query.all()
    cargos = Cargo.query.all()
    equipos = Equipo.query.all()
    niveles_contribucion = NivelContribucion.query.all()  # Cargar los niveles de contribución

    if request.method == 'POST':
        nuevo_usuario = Usuario(
            nombre=request.form['nombre'],
            correo=request.form['correo'],
            contrasena=request.form['contrasena'],
            id_rol=request.form['id_rol'],
            id_cargo=request.form.get('id_cargo') or None,
            id_equipo=request.form.get('id_equipo') or None,
            nivel_contribucion_id=request.form.get('nivel_contribucion') or None  # Asignar nivel de contribución
        )
        db.session.add(nuevo_usuario)
        db.session.commit()
        return redirect(url_for('usuarios_bp.lista_usuarios'))

    return render_template('crear_usuario.html', roles=roles, cargos=cargos, equipos=equipos, niveles_contribucion=niveles_contribucion)



@usuarios_bp.route('/usuarios/editar/<int:usuario_id>', methods=['GET', 'POST'])
def editar_usuario(usuario_id):
    if 'usuario_id' not in session:
        return redirect(url_for('usuarios_bp.login'))
    
    usuario_actual = Usuario.query.get(session['usuario_id'])
    rol_actual = usuario_actual.rol.nombre  # Suponiendo que el modelo Rol tiene un campo 'nombre'

    if rol_actual not in ['Administrador', 'Docente', 'Líder', 'Colaborador']:
        return redirect(url_for('usuarios_bp.dashboard'))
    
    usuario = Usuario.query.get_or_404(usuario_id)
    roles = Rol.query.all()
    cargos = Cargo.query.all()
    equipos = Equipo.query.all()
    niveles_contribucion = NivelContribucion.query.all()  # Cargar los niveles de contribución

    if request.method == 'POST':
        usuario.nombre = request.form['nombre']
        usuario.correo = request.form['correo']
        usuario.contrasena = request.form['contrasena']
        usuario.id_rol = request.form['id_rol']
        usuario.id_cargo = request.form.get('id_cargo') or None
        usuario.id_equipo = request.form.get('id_equipo') or None
        usuario.nivel_contribucion_id = request.form.get('nivel_contribucion') or None  # Actualizar nivel de contribución

        db.session.commit()
        return redirect(url_for('usuarios_bp.lista_usuarios'))

    return render_template('editar_usuario.html', usuario=usuario, roles=roles, cargos=cargos, equipos=equipos, niveles_contribucion=niveles_contribucion)



@usuarios_bp.route('/usuarios/eliminar/<int:usuario_id>', methods=['POST'])
def eliminar_usuario(usuario_id):
    # Comprobar si el usuario tiene el rol adecuado (Administrador, Docente, Líder, Colaborador)
    if 'usuario_id' not in session:
        return redirect(url_for('usuarios_bp.login'))
    
    usuario_actual = Usuario.query.get(session['usuario_id'])
    rol_actual = usuario_actual.rol.nombre  # Suponiendo que el modelo Rol tiene un campo 'nombre'

    # Verificar si el usuario tiene un rol autorizado
    if rol_actual not in ['Administrador', 'Docente', 'Líder', 'Colaborador']:
        return redirect(url_for('usuarios_bp.dashboard'))  # Redirigir a la página principal si no tiene permiso
    
    # Buscar el usuario por ID
    usuario = Usuario.query.get_or_404(usuario_id)

    try:
        # Eliminar el usuario de la base de datos
        db.session.delete(usuario)
        db.session.commit()
        return redirect(url_for('usuarios_bp.lista_usuarios'))  # Redirigir a la lista de usuarios
    except Exception as e:
        db.session.rollback()  # Deshacer cambios si ocurre un error
        return f"Error al eliminar usuario: {str(e)}"


# ========================================================
#                  CONFIGURACIÓN DE CUENTA
# ========================================================

@usuarios_bp.route('/configuracion', methods=['GET', 'POST'])
def configuracion():
    if 'usuario_id' not in session:
        return redirect(url_for('usuarios_bp.login'))

    usuario = Usuario.query.get(session['usuario_id'])

    if request.method == 'POST':
        nuevo_tema = request.form.get('tema')
        nuevo_idioma = request.form.get('idioma')
        nueva_contrasena = request.form.get('contrasena')

        # Si hay tabla de configuración individual, úsala. Si no, modifica usuario directamente.
        if hasattr(usuario, 'config'):
            usuario.config.tema = nuevo_tema
            usuario.config.idioma = nuevo_idioma
        else:
            # Si no hay tabla de config, asumimos que tema/idioma están en Usuario
            if hasattr(usuario, 'tema'):
                usuario.tema = nuevo_tema
            if hasattr(usuario, 'idioma'):
                usuario.idioma = nuevo_idioma

        if nueva_contrasena:
            usuario.contrasena = nueva_contrasena  # ⚠️ En producción, hashea esto con werkzeug o bcrypt

        db.session.commit()
        return redirect(url_for('usuarios_bp.dashboard'))

    return render_template('configuracion.html', usuario=usuario)


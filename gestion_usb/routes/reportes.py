from flask import Blueprint, render_template, request, redirect, url_for, session
from gestion_usb.models import db, Evaluacion, Indicador, ResultadoEvaluacion, Usuario, Seccion
from datetime import date
import plotly.graph_objs as go
import plotly.io as pio
from markupsafe import Markup  # ✅ correcto

reportes_bp = Blueprint('reportes_bp', __name__)

# Ver todas las evaluaciones
@reportes_bp.route('/evaluaciones')
def ver_evaluaciones():
    evaluaciones = Evaluacion.query.all()
    return render_template('evaluaciones.html', evaluaciones=evaluaciones)


# Crear una nueva evaluación (asignar evaluador y evaluado)
@reportes_bp.route('/evaluaciones/crear', methods=['GET', 'POST'])
def crear_evaluacion():
    usuarios = Usuario.query.all()
    if request.method == 'POST':
        evaluacion = Evaluacion(
            fecha=date.today(),
            usuario_id=request.form['usuario_id'],
            evaluador_id=request.form['evaluador_id']
        )
        db.session.add(evaluacion)
        db.session.commit()
        return redirect(url_for('reportes_bp.ver_evaluaciones'))
    return render_template('crear_evaluacion.html', usuarios=usuarios)


# Responder evaluación (ingresar valores por indicador)
@reportes_bp.route('/evaluaciones/responder/<int:evaluacion_id>', methods=['GET', 'POST'])
def responder_evaluacion(evaluacion_id):
    evaluacion = Evaluacion.query.get_or_404(evaluacion_id)
    secciones = Seccion.query.all()
    indicadores = Indicador.query.all()

    if request.method == 'POST':
        for indicador in indicadores:
            valor = float(request.form.get(f"valor_{indicador.id}", 0))
            resultado = ResultadoEvaluacion(
                evaluacion_id=evaluacion_id,
                indicador_id=indicador.id,
                valor=valor
            )
            db.session.add(resultado)
        db.session.commit()
        return redirect(url_for('reportes_bp.ver_evaluaciones'))

    return render_template('responder_evaluacion.html', evaluacion=evaluacion, secciones=secciones, indicadores=indicadores)


# Ver resultados de una evaluación
@reportes_bp.route('/evaluaciones/resultados/<int:evaluacion_id>')
def resultados_evaluacion(evaluacion_id):
    evaluacion = Evaluacion.query.get_or_404(evaluacion_id)
    resultados = ResultadoEvaluacion.query.filter_by(evaluacion_id=evaluacion_id).all()
    return render_template('resultados_evaluacion.html', evaluacion=evaluacion, resultados=resultados)

@reportes_bp.route('/dashboard_reportes')
def dashboard_reportes():
    usuario = session.get('usuario')
    return render_template('dashboard_reportes.html', usuario=usuario)


@reportes_bp.route('/dashboard_reportes/crecimiento')
def crecimiento():
    indicadores = Indicador.query.filter(Indicador.nombre.ilike('%crecimiento%')).all()

    datos_graficos = []

    for indicador in indicadores:
        resultados = ResultadoEvaluacion.query.filter_by(indicador_id=indicador.id).all()
        fechas = [res.evaluacion.fecha.strftime('%Y-%m-%d') for res in resultados]
        valores = [res.valor for res in resultados]

        trace = go.Scatter(x=fechas, y=valores, mode='lines+markers', name=indicador.nombre)
        datos_graficos.append(trace)

    layout = go.Layout(
        title='Indicadores de Crecimiento a lo largo del tiempo',
        xaxis=dict(title='Fecha'),
        yaxis=dict(title='Valor'),
        template='plotly_white'
    )

    fig = go.Figure(data=datos_graficos, layout=layout)
    grafico_html = pio.to_html(fig, full_html=False)

    return render_template(
        'crecimiento.html',
        usuario=session.get('usuario'),
        grafico=Markup(grafico_html),
        indicadores=indicadores
    )

from gestion_usb.models import RespuestaDimension, Dimension, Pregunta, Respuesta
from sqlalchemy import func

@reportes_bp.route('/dashboard_reportes/analisis_organizacional')
def analisis_organizacional():
    usuario = session.get('usuario')

    datos_agrupados = db.session.query(
        RespuestaDimension.id_dimension,
        RespuestaDimension.fecha_respuesta,
        func.avg(Respuesta.id).label('promedio')
    ).join(Respuesta, Respuesta.id == RespuestaDimension.id_respuesta) \
     .group_by(RespuestaDimension.id_dimension, RespuestaDimension.fecha_respuesta) \
     .order_by(RespuestaDimension.fecha_respuesta.asc()) \
     .all()

    datos_por_dimension = {}
    for dim_id, fecha, promedio in datos_agrupados:
        nombre_dim = Dimension.query.get(dim_id).nombre
        fecha_str = fecha.strftime('%Y-%m-%d')

        if nombre_dim not in datos_por_dimension:
            datos_por_dimension[nombre_dim] = {'fechas': [], 'valores': []}
        datos_por_dimension[nombre_dim]['fechas'].append(fecha_str)
        datos_por_dimension[nombre_dim]['valores'].append(round(promedio, 2))

    # Crear gráfico Plotly
    trazas = []
    for dimension, datos in datos_por_dimension.items():
        trazas.append(go.Scatter(
            x=datos['fechas'],
            y=datos['valores'],
            mode='lines+markers',
            name=dimension
        ))

    layout = go.Layout(
        title='Análisis Organizacional por Dimensión',
        xaxis=dict(title='Fecha'),
        yaxis=dict(title='Promedio de Respuestas'),
        template='plotly_white'
    )

    fig = go.Figure(data=trazas, layout=layout)
    grafico_html = pio.to_html(fig, full_html=False)

    return render_template(
        'analisis_organizacional_dashboard.html',
        usuario=usuario,
        grafico=Markup(grafico_html),
        resumen=datos_por_dimension
    )
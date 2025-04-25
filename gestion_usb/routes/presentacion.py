from flask import Blueprint, render_template

presentacion_bp = Blueprint('presentacion_bp', __name__, template_folder='templates')

@presentacion_bp.route('/presentacion', methods=['GET', 'POST'])
def ver_presentacion():
    return render_template('presentacion.html')


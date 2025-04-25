from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from dotenv import load_dotenv
import os

from gestion_usb.models import db  # Esta es la instancia original

load_dotenv()

app = Flask(__name__, template_folder='gestion_usb/templates', static_folder='gestion_usb/static')
app.secret_key = '123456789'
#app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:ainoaboleavilla@localhost:5432/backupBDGD'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:pgadmin4@localhost:5432/bdgestionnuevo'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# ✅ Solo inicializas la instancia ya importada
db.init_app(app)
migrate = Migrate(app, db)

# Importar modelos y blueprints
from gestion_usb.routes.usuarios import usuarios_bp
from gestion_usb.routes.desempeno import desempeno_bp
from gestion_usb.routes.desarrollo import desarrollo_bp
from gestion_usb.routes.reportes import reportes_bp
from gestion_usb.routes.presentacion import presentacion_bp

app.register_blueprint(presentacion_bp)
app.register_blueprint(usuarios_bp)
app.register_blueprint(desempeno_bp)
app.register_blueprint(desarrollo_bp)
app.register_blueprint(reportes_bp)

if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, Blueprint, render_template

from flask_migrate import Migrate

from config import DevelopmentConfig

from api.router import apiRouter

frontendRouter = Blueprint('app', __name__, url_prefix='/app') # handles /app

@frontendRouter.route("/")
def frontend():
    return render_template('index.html')

def create_app() -> Flask:
    app = Flask(__name__, static_folder='../frontend/build/static', template_folder='../frontend/build') # serve compiled react app.

    app.config.from_object(DevelopmentConfig)

    # --- DB
    from models import db

    db.app = app

    db.init_app(app)

    Migrate(app,db)    
    # --- DB

    # --- ROUTERS
    app.register_blueprint(apiRouter) # api
    app.register_blueprint(frontendRouter) # frontend
    # --- ROUTERS

    # -- QUERY EXAMPLE

    # from models.User import User,Patient

    # patients = Patient.query.all()

    # for u in patients:
    #     print(f'CI: {u.ci} firstName: {u.base.name1}')

    # for phoneNumber in u.base.phoneNumbers:
    #     print(f' /// phone: {phoneNumber.phone}')

    return app

if __name__ == '__main__':
    create_app().run()
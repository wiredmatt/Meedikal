from flask import Blueprint, render_template
from api.user import router as userRouter # handles /api/user
from api.appointment import router as appointmentRouter # handles /api/appointment
from api.branch import router as branchRouter # handles /api/branch
from api.auth import router as authRouter # handles /api/auth
# modular routing, instead of having all the routes in this file, I'm making multiple routers that handle each table of the database. 

apiRouter = Blueprint('api', __name__, url_prefix='/api') # handles /api

apiRouter.register_blueprint(authRouter)
apiRouter.register_blueprint(userRouter)
apiRouter.register_blueprint(appointmentRouter) 
apiRouter.register_blueprint(branchRouter)

frontendRouter = Blueprint('frontend', __name__, url_prefix='/') # handles /

@frontendRouter.route('/')
@frontendRouter.route('/<path:path>')
def frontend(path=None):
    return render_template('index.html')
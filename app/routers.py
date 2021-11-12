import os
from config import Config
from flask import Blueprint, send_file
from api.users import router as usersRouter # handles /api/user
from api.appointments import router as appointmentsRouter # handles /api/appointment
from api.branches import router as branchesRouter # handles /api/branch
from api.auth import router as authRouter # handles /api/auth
from api.sufferings import router as sufferingsRouter # handles /api/suffering
from api.pagination import router as paginationRouter # handles /api/pagination
from frontend.router import frontendRouter
# modular routing, instead of having all the routes in this file, I'm making multiple routers that handle each table of the database. 

apiRouter = Blueprint('api', __name__, url_prefix='/api') # handles /api

apiRouter.register_blueprint(authRouter)
apiRouter.register_blueprint(usersRouter)
apiRouter.register_blueprint(appointmentsRouter) 
apiRouter.register_blueprint(branchesRouter)
apiRouter.register_blueprint(sufferingsRouter)
apiRouter.register_blueprint(paginationRouter)

imagesRouter = Blueprint('images', __name__, url_prefix='/images') # handles /images
@imagesRouter.get('/<resource>')
def returnResource(resource:str):
    return send_file(os.path.join(Config.UPLOAD_FOLDER, resource))
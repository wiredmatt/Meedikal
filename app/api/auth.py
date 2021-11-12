from flask import Blueprint, session

from middleware.data import passJsonData
from middleware.authGuard import requiresAuth, requiresRole, getCurrentRole
from models.User import User, AuthUser
from .users import userToReturn
from util.crud import crudReturn
from util.returnMessages import genericErrorReturn

router = Blueprint('auth', __name__, url_prefix='/auth')

@router.post('/login') # POST /api/auth/login
@passJsonData
def login(data:dict):
    token = AuthUser.login(data['id'], data['password'])

    if token is None:
        return genericErrorReturn('incorrect ID or password')
    else:
        session['authToken'] = token
        session['currentRole'] = User.getRoles(data['id'])[0]
        return crudReturn('OK')

@router.post('/logout') # POST /api/auth/logout
@requiresAuth
def logout(**kwargs):
    session.pop('authToken', None)
    session.pop('currentRole', None)
    return crudReturn('OK')

@router.get('/me')
@getCurrentRole
def me(id:int, currentRole:str, **kw):
    user = User.select({'id': id}, shape='one')
    return crudReturn(userToReturn(user, id, currentRole, currentRole))

@router.route('/updatePassword', methods=['PUT', 'PATCH']) # POST /api/auth/updatePassword
@requiresAuth
@passJsonData
def updatePassword(id:int,data:dict):
    res = User.updatePassword(id,data['password'])
    return crudReturn(res)

@router.get('/currentRole')
@getCurrentRole
def returnCurrentRole(currentRole:str, *args, **kwargs):
    return crudReturn(currentRole)

@router.post('/currentRole/<string:role>')
def setCurrentRole(role:str):
    @requiresRole([role]) # to change to the desired role, the user should have it already
    def withinFlaskContext():
        session['currentRole'] = role
        return crudReturn(session['currentRole'])
    return withinFlaskContext()
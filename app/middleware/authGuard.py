from util.errors import MissingCookieError, MissingRoleError, InactiveUserError
from flask import session
from models.User import User, AuthUser
from functools import wraps

def requiresAuth(f):
    @wraps(f)
    def decorator(*args,**kwargs):
        token = None
        try:
            token = session.get('authToken', None)
        except: # flask out of context error (raises when starting the app)
            pass

        if token is None:
            raise MissingCookieError()
        else:
            id = int(AuthUser.verifyToken(token))
            user: User = User.select({'id': id}, shape='one')
            if not user.active:
                raise InactiveUserError
                
            return f(*args, **kwargs, id=id)
        
    return decorator

def requiresRole(roles:list[str]): # the required roles to execute the action
    def decorator(f):
        @requiresAuth
        @wraps(f)
        def wrapper(id:int,*args, **kwargs): # id comes from the previous deco: requiresAuth
            userRoles = User.getRoles(id)

            if 'idUser' in [k for k in kwargs.keys()]:
                if kwargs['idUser'] == id:
                    return f(*args, **kwargs)

            for r in roles:
                if r in userRoles:
                    return f(*args, **kwargs)

            raise MissingRoleError(roles)

        return wrapper

    return decorator

def getCurrentRole(f):
    @requiresAuth
    @wraps(f)
    def wrapper(id:int,*args, **kwargs): # id comes from the previous deco: requiresAuth
        currentRole = session.get('currentRole', None)
            
        if not currentRole:
            currentRole = User.getRoles(id)[0]
            session['currentRole'] = currentRole

        return f(*args, **kwargs, currentRole=currentRole, id=id)
    return wrapper
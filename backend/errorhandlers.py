from routers import apiRouter
from util.returnMessages import *
from util.errors import *
from sqlite3.dbapi2 import IntegrityError
from util.createDb import getDb
import jwt

@apiRouter.errorhandler(jwt.ExpiredSignatureError)
def expiredToken(e):
    return genericErrorReturn('Signature expired. Please log in again.', code=401)

@apiRouter.errorhandler(jwt.InvalidTokenError)
def invalidToken(e):
    return genericErrorReturn('Invalid token. Please log in again.', code=401)

@apiRouter.errorhandler(MissingCookieError)
def missingCookieError(e):
    return genericErrorReturn('Not authenticated (missing cookie)', code=401)

@apiRouter.errorhandler(MissingRoleError)
def missingRoleError(e: MissingRoleError):
    return genericErrorReturn(f'Insufficient permissions to perfom action. It should be done by: a {e.role} user', code=403)

@apiRouter.errorhandler(UpdatePasswordError)
def updatePasswordError(e):
    return genericErrorReturn(f"can't update password with this method. PUT or PATCH the api/auth/updatePassword endpoint instead.", code=403)

@apiRouter.errorhandler(TypeError)
def typeError(e:TypeError):
    err = repr(e)
    extraMessage = None
    print(e)

    if 'missing' in err:
        extraMessage = err.split(': ')[1].split('")')[0]
    return provideData(extraMessage)

@apiRouter.errorhandler(KeyError)
def keyError(e:KeyError):
    return provideData(f'missing required fields: {", ".join(e.args)}')

@apiRouter.errorhandler(IntegrityError)
def integrityError(e:IntegrityError):
    err = repr(e)
    getDb().rollback()

    if 'FOREIGN KEY' in err:
        return genericErrorReturn(f"foreign key error: one of the values you are referring to was deleted or never existed")
    else:       
        errData = err.split('.')
        tablename = errData[0].split(": ")[1]
        attr = errData[1].split("')")[0]

        if 'UNIQUE' in err:        
            return recordAlreadyExists(tablename, attr)
        elif 'NOT NULL' in err:
            return provideData(f'missing required field: {attr} for {tablename}')

@apiRouter.errorhandler(Exception) # any other exception
def handle_exception(e:Exception):
    err = repr(e)
    print(err)
    getDb().rollback()
    return {"error": repr(err)}, 400
from functools import wraps
from flask import Blueprint
from models.Branch import *
from util.crud import *
from middleware.authGuard import requiresRole, requiresAuth
from middleware.data import passJsonData, paginated, resourceExists, validDataValues
from .appointments import appointmentExists

router = Blueprint('branches', __name__, url_prefix='/branches')

def branchExists(idFields=['id'], idArgs=['idB'], abort=True):
    def decorator(f):
        @resourceExists(Branch, idFields, idArgs, abort)
        @wraps(f)
        def wrapper(obj, *args,**kwargs):
            return f(*args, **kwargs, branch=obj)
        
        return wrapper
    return decorator

@router.get('/<int:idB>')
@requiresAuth
@branchExists()
def getBranchById(branch:Branch, **kwargs):
    return crudReturn(branch)

@router.get('/<string:name>')
@requiresAuth
@paginated()
def getBranchByName(name:str, offset:int, limit:int, **kwargs):
    branches = Branch.selectMany({'name': {'value': name, 'operator': 'LIKE'}}, offset=offset, limit=limit)
    return crudReturn(branches)

@router.get('/all') # public endpoint
def getAllBranches():
    return crudReturn(Branch.selectAll())

@router.post('')
@passJsonData
@requiresRole(['administrative'])
def createBranch(data:dict, **kw):
    return crudReturn(Branch(**data).insert())

@router.route('/<int:idB>', methods=['PUT', 'PATCH']) 
@passJsonData
@requiresRole(['administrative'])
@branchExists()
def updateBranchById(branch:Branch, data:dict, **kwargs):
    return crudReturn(branch.update(data))

@router.delete('/<int:idB>')
@requiresRole(['administrative'])
@branchExists()
def deleteBranch(branch:Branch, **kwargs):
    return crudReturn(branch.delete())

@router.post('/apTakesPlace/<int:idAp>/<int:idB>')
@requiresRole(['administrative'])
@branchExists()
@appointmentExists()
def createApTakesPlace(data:dict, **kwargs):
    return crudReturn(ApTakesPlace(**data).insert())

@router.get('/apTakesPlace/<int:idAp>')
@requiresAuth
@appointmentExists(ApTakesPlace)
def getApTakesPlace(obj:ApTakesPlace, **kwargs):
    return crudReturn(obj)

@router.route('/apTakesPlace/<int:idAp>', methods=['PUT', 'PATCH'])
@requiresRole(['administrative'])
@appointmentExists(ApTakesPlace)
@validDataValues(Branch, ['id'], ['idBranch'])
@passJsonData
def updateApTakesPlace(obj:ApTakesPlace, data:dict, **kwargs):
    data.pop('idAp', None)
    return crudReturn(obj.update(data))
from dataclasses import asdict
from functools import wraps
from flask import Blueprint, request
from flask.json import jsonify
from util.errors import InvalidSufferingType
from util.crud import crudReturn
from models._base import BaseModel
from models.ClinicalSign import ClinicalSign
from models.Disease import Disease
from models.Symptom import Symptom
from middleware.authGuard import requiresRole, requiresAuth
from middleware.data import paginated, passJsonData, resourceExists

router = Blueprint('sufferings', __name__, url_prefix='/sufferings')

sufferingMappings:dict[str, BaseModel] = {"symptom": Symptom, "clinicalSign": ClinicalSign, "disease": Disease}

def validSufferingType(s:str) -> BaseModel:
    if sufferingMappings.get(s, None) is not None:
        return sufferingMappings[s]
    else:
        raise InvalidSufferingType

def sufferingExists(idFields=['id'], idArgs=['idS'], abort=True):
    def decorator(f):
        @wraps(f)
        def wrapper(sufferingType:str=None, *args, **kwargs): # request.view_args['sufferingType']            
            @resourceExists(Model=validSufferingType(sufferingType), idFields=idFields, idArgs=idArgs, abort=abort)
            def x(obj=None):
                return f(suffering=obj, *args, **kwargs)
            
            return x()
        return wrapper
    return decorator

@router.route('/search/<string:sufferingType>', methods=['GET','POST'])
@requiresAuth
@paginated()
def searchSuffering(sufferingType:str, offset:int, limit:int, data:dict={}, **kw):
    result = validSufferingType(sufferingType).selectMany(data, 'OR', offset=offset, limit=limit)

    if len(result) > 0:
        for r in result:
            if r.description is not None:
                if len(r.description) > 27:
                  r.description = r.description[:26] + '..' # make it so the description of each suffering in the response has no more than 30 characters.
 
        result = [asdict(r) for r in result]

    return crudReturn(result)

@router.post('/<string:sufferingType>')
@requiresRole(['doctor', 'administrative'])
@passJsonData
def createSuffering(sufferingType:str, data:dict={}, **kwargs):
    result = validSufferingType(sufferingType)(**data).insert()
    return crudReturn(result)

@router.route('/<string:sufferingType>/<int:idS>', methods=['PUT', 'PATCH'])
@requiresRole(['doctor', 'administrative'])
@passJsonData
@sufferingExists()
def updateSuffering(suffering:BaseModel=None, data:dict={}, *args, **kwargs):
    result = suffering.update(data)
    return crudReturn(result)

@router.delete('/<string:sufferingType>/<int:idS>')
@requiresRole(['doctor', 'administrative'])
@sufferingExists()
def deleteSuffering(suffering:BaseModel, **kwargs):
    return crudReturn(suffering.delete())
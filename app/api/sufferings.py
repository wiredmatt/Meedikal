from dataclasses import asdict
from functools import wraps
from flask import Blueprint
from util.errors import InvalidSufferingType
from util.crud import crudReturn
from models._base import BaseModel
from models.ClinicalSign import *
from models.Disease import *
from models.Symptom import *
from models.Appointment import AttendsTo
from middleware.authGuard import requiresRole, requiresAuth
from middleware.data import paginated, passJsonData, resourceExists, validDataValues

router = Blueprint('sufferings', __name__, url_prefix='/sufferings')

sufferingMappings:dict[str, BaseModel] = {"symptom": Symptom, "clinicalSign": ClinicalSign, "disease": Disease}

def validSufferingType(s:str) -> BaseModel:
    if sufferingMappings.get(s, None) is not None:
        return sufferingMappings[s]
    else:
        raise InvalidSufferingType

def sufferingExists(idFields=['id'], idArgs=['idS'], abort=True, Model:BaseModel=None):
    def decorator(f):
        @wraps(f)
        def wrapper(sufferingType:str=None, *args, **kwargs): # request.view_args['sufferingType']            
            @resourceExists(Model=Model if Model is not None else validSufferingType(sufferingType), idFields=idFields, idArgs=idArgs, abort=abort)
            def passSf(obj=None):
                return f(suffering=obj, *args, **kwargs)
            
            return passSf()
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

def passSuffering(Model:BaseModel, idField:str, nameField:str='name'):
    def decorator(f):
        @wraps(f)
        @passJsonData
        def wrapper(data:dict, *args,**kwargs):
            if data.get(idField, None) is None:
                _entity = Model.insertOrSelect({nameField: data[nameField]})
                data[idField] = _entity.id
                data.pop(nameField)
            return f(*args, **kwargs, data=data)
        
        return wrapper
    return decorator

@router.post('/registersSy')
@requiresRole(['doctor', 'administrative'])
@passSuffering(Symptom, 'idSy')
@validDataValues(AttendsTo, ['idAp', 'idPa'], ['idAp', 'idPa'])
@passJsonData
def createRegistersSy(data:dict, **kwargs):
    return crudReturn(RegistersSy(**data).insert())

@router.delete('/registersSy')
@requiresRole(['doctor', 'administrative'])
@passSuffering(RegistersSy, 'idSy')
@validDataValues(RegistersSy, ['idAp', 'idPa', 'idSy'], ['idAp', 'idPa', 'idSy'])
@passJsonData
def deleteRegistersSy(data:dict, **kwargs):
    return crudReturn(RegistersSy.selectOne(data).delete())

@router.get('/registersSy/<int:idAp>/<int:idPa>')
@requiresRole(['self', 'doctor', 'administrative'])
@passJsonData
def getRegistersSy(idAp:int, idPa:int, **kwargs):
    return crudReturn(RegistersSy.selectMany({'idAp': idAp, 'idPa': idPa}))

@router.post('/registersCs')
@requiresRole(['doctor', 'administrative'])
@passSuffering(ClinicalSign, 'idCs')
@validDataValues(AttendsTo, ['idAp', 'idPa'], ['idAp', 'idPa'])
@passJsonData
def createRegistersCs(data:dict, **kwargs):
    return crudReturn(RegistersCs(**data).insert())

@router.delete('/registersCs')
@requiresRole(['doctor', 'administrative'])
@passSuffering(RegistersCs, 'idCs')
@validDataValues(RegistersCs, ['idAp', 'idPa', 'idCs'], ['idAp', 'idPa', 'idCs'])
@passJsonData
def deleteRegistersCs(data:dict, **kwargs):
    return crudReturn(RegistersCs.selectOne(data).delete())

@router.get('/registersCs/<int:idAp>/<int:idPa>')
@requiresRole(['self', 'doctor', 'administrative'])
@passJsonData
def getRegistersCs(idAp:int, idPa:int, **kwargs):
    return crudReturn(RegistersCs.selectMany({'idAp': idAp, 'idPa': idPa}))

@router.post('/diagnoses')
@requiresRole(['doctor', 'administrative'])
@passSuffering(Disease, 'idDis')
@validDataValues(AttendsTo, ['idAp', 'idPa'], ['idAp', 'idPa'])
@passJsonData
def createDiagnoses(data:dict, **kwargs):
    return crudReturn(Diagnoses(**data).insert())

@router.delete('/diagnoses')
@requiresRole(['doctor', 'administrative'])
@passSuffering(Diagnoses, 'idDis')
@validDataValues(Diagnoses, ['idAp', 'idPa', 'idDis'], ['idAp', 'idPa', 'idDis'])
@passJsonData
def deleteDiagnoses(data:dict, **kwargs):
    return crudReturn(Diagnoses.selectOne(data).delete())

@router.get('/diagnoses/<int:idAp>/<int:idPa>')
@requiresRole(['self', 'doctor', 'administrative'])
@passJsonData
def getDiagnoses(idAp:int, idPa:int, **kwargs):
    return crudReturn(Diagnoses.selectMany({'idAp': idAp, 'idPa': idPa}))
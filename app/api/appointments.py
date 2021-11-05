from flask import Blueprint
from dataclasses import asdict
from functools import wraps
from models.User import Doctor, User
from models.Appointment import *
from models.Branch import Branch
from models.ClinicalSign import ClinicalSign, RegistersCs
from models.Disease import Disease, Diagnoses
from models.Symptom import Symptom, RegistersSy
from models.Branch import *
from util.crud import *
from util.returnMessages import *
from middleware.authGuard import requiresRole, requiresAuth, getCurrentRole
from middleware.data import passJsonData, paginated, resourceExists
from models import db
from .users import userToReturn

router = Blueprint('appointments', __name__, url_prefix='/appointments')

def appointmentExists(idFields=['id'], idArgs=['idAp'], abort=True):
    def decorator(f):
        @resourceExists(Appointment, idFields, idArgs, abort)
        @wraps(f)
        def wrapper(obj, *args,**kwargs):
            return f(*args, **kwargs, appointment=obj)
        
        return wrapper
    return decorator

def apRelationExists(Model=BaseModel,idFields=['idAp'], idArgs=['idAp'], abort=True):
    def decorator(f):
        @resourceExists(Model, idFields, idArgs, abort)
        @wraps(f)
        def wrapper(obj, *args,**kwargs):
            return f(*args, **kwargs, obj=obj)
        
        return wrapper
    return decorator

@router.route('/all', methods=['GET', 'POST'])
@requiresAuth
@paginated()
def all(offset:int, limit:int, data:dict=None, **kwargs):
    return crudReturn(Appointment.selectMany(data, offset=offset, limit=limit))

@router.get('/<int:idAp>')
@requiresAuth
@appointmentExists()
def getAppointmentById(appointment:Appointment, **kwargs):
    return crudReturn(appointment)

@router.post('')
@requiresRole(['administrative'])
@passJsonData
def createAppointment(data:dict, **kwargs):
    return crudReturn(Appointment(**data).insert())

@router.route('/<int:idAp>', methods=['PUT', 'PATCH'])
@requiresRole(['administrative'])
@appointmentExists()
def updateAppointment(appointment:Appointment,data:dict, **kwargs):
    return crudReturn(appointment.update(data))

@router.route('/<int:idAp>', methods=['PUT', 'PATCH'])
@requiresRole(['administrative'])
@appointmentExists()
def updateAppointmentById(appointment:Appointment, data:dict, **kw):
    return crudReturn(appointment.update(data))

@router.delete('/<int:idAp>') 
@requiresRole(['administrative'])
@appointmentExists()
def deleteAppointment(appointment:Appointment, **kwargs):
    return crudReturn(appointment.delete())

@router.post('/apTakesPlace/<int:idAp>/<int:idB>')
@requiresRole(['administrative'])
@passJsonData
def createApTakesPlace(data:dict, **kwargs):
    return crudReturn(ApTakesPlace(**data).insert())

@router.get('/apTakesPlace/<int:idAp>')
@requiresAuth
@apRelationExists(ApTakesPlace)
def getApTakesPlace(obj:ApTakesPlace, **kwargs):
    return crudReturn(obj)

@router.route('/apTakesPlace/<int:idAp>', methods=['PUT', 'PATCH'])
@passJsonData
@requiresRole(['administrative'])
@apRelationExists(ApTakesPlace)
def updateApTakesPlace(obj:ApTakesPlace, data:dict, **kwargs):
    return crudReturn(obj.update(data))

# -- Users <> appointment

@router.post('/assignedTo')
@requiresRole(['administrative'])
@passJsonData
def createAssignedTo(data:dict, **kwargs):
    return crudReturn(AssignedTo(**data).insert())

@router.route('/assignedTo/<int:idAp>/<int:idDoc>', methods=['PUT', 'PATCH'])
@requiresRole(['administrative'])
@passJsonData
@apRelationExists(AssignedTo, ['idAp', 'idDoc'], ['idAp', ['idDoc']])
def updateAssignedTo(obj:AssignedTo, data:dict, **kwargs):
    return crudReturn(obj.update(data))

@router.get('/assignedTo/<int:idAp>')
@router.get('/assignedTo/idDoc/<int:idDoc>')
@requiresAuth
@paginated()
def getAssignedTo(idAp:int=None, idDoc:int=None, **kwargs): 
    if idAp:
        return crudReturn(AssignedTo.selectOne({'idAp': idAp}))
    else:
        return crudReturn(AssignedTo.selectMany({'idDoc': idDoc}))
        
@router.post('/attendsTo')
@requiresRole(['administrative'])
@passJsonData
def createAttendsTo(data:dict, **kwargs):
    return crudReturn(AttendsTo(**data).insert())

@router.route('/attendsTo/<int:idAp>/<int:idPa>', methods=['PUT', 'PATCH'])
@requiresRole(['administrative'])
@passJsonData
@apRelationExists(AttendsTo, ['idAp', 'idPa'], ['idAp', ['idPa']])
def updateAttendsTo(obj:AttendsTo, data:dict, **kwargs):
    return crudReturn(obj.update(data))

@router.get('/attendsTo/<int:idAp>')
@router.get('/attendsTo/idPa/<int:idPa>')
@requiresAuth
@paginated()
def getAttendsTo(idAp:int=None, idPa:int=None, **kwargs): 
    if idAp:
        return crudReturn(AttendsTo.selectOne({'idAp': idAp}))
    else:
        return crudReturn(AttendsTo.selectMany({'idPa': idPa}))

@router.delete('/attendsTo/<int:idAp>/<int:idPa>')
@requiresRole(['administrative'])
@passJsonData
@apRelationExists(AttendsTo, ['idAp', 'idPa'], ['idAp', 'idPa'])
def deleteAttendsTo(obj:AttendsTo, **kwargs):
    return crudReturn(obj.delete())

# # -- DATA INPUTTED WHEN A PATIENT IS BEING INTERVIEWED IN AN APPOINTMENT

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
@passJsonData
@passSuffering(Symptom, 'idSy')
def createRegistersSy(data:dict, **kwargs):
    return crudReturn(RegistersSy(**data).insert())

@router.delete('/registersSy')
@requiresRole(['doctor', 'administrative'])
@passJsonData
@passSuffering(RegistersSy, 'idSy')
def deleteRegistersSy(data:dict, **kwargs):
    return crudReturn(RegistersSy.selectOne({'idAp' : data['idAp'], 'idPa' : data['idPa'], 'idSy' : data['idSy']}).delete())

@router.get('/registersSy/<int:idAp>/<int:idPa>')
@requiresRole(['self', 'doctor', 'administrative'])
@passJsonData
def getRegistersSy(idAp:int, idPa:int, **kwargs):
    return crudReturn(RegistersSy.selectMany({'idAp': idAp, 'idPa': idPa}))

@router.post('/registersCs')
@requiresRole(['doctor', 'administrative'])
@passJsonData
@passSuffering(ClinicalSign, 'idCs')
def createRegistersCs(data:dict, **kwargs):
    return crudReturn(RegistersCs(**data).insert())

@router.delete('/registersCs')
@requiresRole(['doctor', 'administrative'])
@passJsonData
@passSuffering(RegistersCs, 'idCs')
def deleteRegistersCs(data:dict, **kwargs):
    return crudReturn(RegistersCs.selectOne({'idAp' : data['idAp'], 'idPa' : data['idPa'], 'idCs' : data['idCs']}).delete())

@router.get('/registersCs/<int:idAp>/<int:idPa>')
@requiresRole(['self', 'doctor', 'administrative'])
@passJsonData
def getRegistersCs(idAp:int, idPa:int, **kwargs):
    return crudReturn(RegistersCs.selectMany({'idAp': idAp, 'idPa': idPa}))

@router.post('/diagnoses')
@requiresRole(['doctor', 'administrative'])
@passJsonData
@passSuffering(Disease, 'idDis')
def createDiagnoses(data:dict, **kwargs):
    return crudReturn(Diagnoses(**data).insert())

@router.delete('/diagnoses')
@requiresRole(['doctor', 'administrative'])
@passJsonData
@passSuffering(Diagnoses, 'idDis')
def deleteDiagnoses(data:dict, **kwargs):
    return crudReturn(Diagnoses.selectOne({'idAp' : data['idAp'], 'idPa' : data['idPa'], 'idDis' : data['idDis']}).delete())

@router.get('/diagnoses/<int:idAp>/<int:idPa>')
@requiresRole(['self', 'doctor', 'administrative'])
@passJsonData
def getDiagnoses(idAp:int, idPa:int, **kwargs):
    return crudReturn(Diagnoses.selectMany({'idAp': idAp, 'idPa': idPa}))

@router.post('/filter')
@getCurrentRole
@paginated()
def filterAps(id:int, offset:int, limit:int, currentRole:str, data:dict={}, **kwargs): # return appointment, doctor, branch, and (if querying as patient), if you're already scheduled for this appointment.
    _selectedDate = data['selectedDate']
    _from = data['timeInterval']['from']
    _to = data['timeInterval']['to']
    _timeFilter = data['timeFilter']
    _typeFilter = data['typeFilter']
    _doctorSurname1 = data.get('doctorSurname1', None)
    _appointmentName = data.get('appointmentName', None)
    _id = data.get('id', None)

    if (currentRole == 'patient' and _typeFilter == 'mine+doctor') or currentRole != 'patient': # doctors and administrative users can see the appointments of other users, but a patient cannot see appointments of other patients (only of doctors).
        if _id:
            id = _id

    tables = ['appointment']
    conditions = []
    values = []

    if _timeFilter == 'selectedDay' or _timeFilter == 'selectedMonth':
        conditions.append('appointment.date >= ? and appointment.date <= ?') # ?1: _from, ?2: _to
        values.append(_from)
        values.append(_to)
    elif _timeFilter == 'future':
        conditions.append('appointment.date >= ?') # ?1: _selectedDate
        values.append(_selectedDate)
    elif _timeFilter == 'past':
        conditions.append('appointment.date <= ?') # ?1: _selectedDate
        values.append(_selectedDate)
    if _appointmentName:
        conditions.append("appointment.name LIKE ?")
        values.append(_appointmentName)
    
    if _typeFilter == 'mine':
        conditions.append('attendsTo.idPa = ?') 
        conditions.append('attendsTo.idAp = appointment.id') 
        tables.append('attendsTo')
        values.append(id)
    elif _typeFilter == 'mine+doctor':
        conditions.append('assignedTo.idDoc = ?')
        conditions.append('assignedTo.idAp = appointment.id')
        tables.append('assignedTo')
        values.append(id)

    if _doctorSurname1:
        conditions.append("user.surname1 LIKE ?")
        conditions.append("user.id = doctor.id")
        conditions.append('assignedTo.idDoc = doctor.id')
        conditions.append('assignedTo.idAp = appointment.id')
        tables.append('assignedTo')
        tables.append('doctor')
        tables.append('user')
        values.append(_doctorSurname1)

    statementData = f"""
    SELECT appointment.* FROM {', '.join(tables)}
    {' WHERE ' + ' AND '.join(conditions) if len(conditions) > 0 else ''}
    LIMIT {limit} OFFSET {offset}
    """

    statementCount = f"""
    SELECT COUNT(appointment.id) FROM {', '.join(tables)}
    {' WHERE ' + ' AND '.join(conditions) if len(conditions) > 0 else ''}
    """

    resultData = [{'appointment': asdict(Appointment(*ap))} for ap in db.execute(statementData, values).fetchall()]

    resultCount = db.execute(statementCount, values).fetchone()[0]
    
    for r in resultData:
        doc = Doctor.getDocOfAp(r['appointment']['id'])
        br = Branch.getBranchOfAp(r['appointment']['id'])

        if isinstance(doc, User):
            r['doctor'] = userToReturn(doc, id, **kwargs)

        if isinstance(br, Branch):
            r['branch'] = asdict(br)

        if _typeFilter == 'mine':
            imAttending = AttendsTo.selectOne({'idAp': r['appointment']['id'], 'idPa': _id})
            r['imAttending'] = isinstance(imAttending, AttendsTo) # indicates whether the patient is already scheduled for this appointment or not

    return crudReturn(resultData, {'total': resultCount})
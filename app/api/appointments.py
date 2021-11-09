from flask import Blueprint
from dataclasses import asdict
from functools import wraps
from models import db
from models.User import Doctor, User
from models.Appointment import *
from models.Branch import Branch
from util.crud import *
from util.returnMessages import *
from middleware.authGuard import requiresRole, requiresAuth, getCurrentRole
from middleware.data import passJsonData, paginated, resourceExists, validDataValues
from .users import userToReturn

router = Blueprint('appointments', __name__, url_prefix='/appointments')

def appointmentExists(Model=Appointment, idFields=['id'], idArgs=['idAp'], abort=True):
    def decorator(f):
        @resourceExists(Model, idFields, idArgs, abort)
        @wraps(f)
        def wrapper(obj, *args,**kwargs):
            return f(*args, **kwargs, appointment=obj)
        
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

@router.post('/assignedTo')
@requiresRole(['administrative'])
@validDataValues(Appointment, ['id'], ['idAp'])
@validDataValues(Doctor, ['id'], ['idDoc'])
@passJsonData
def createAssignedTo(data:dict, **kwargs):
    return crudReturn(AssignedTo(**data).insert())

@router.route('/assignedTo/<int:idAp>/<int:idDoc>', methods=['PUT', 'PATCH'])
@requiresRole(['administrative'])
@appointmentExists(AssignedTo, ['idAp', 'idDoc'], ['idAp', 'idDoc'])
@validDataValues(Doctor, ['id'], ['idDoc'])
@passJsonData
def updateAssignedTo(obj:AssignedTo, data:dict, **kwargs):
    data.pop('idAp', None)
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
@validDataValues(Appointment, ['id'], ['idAp'])
@validDataValues(Patient, ['id'], ['idPa'])
@passJsonData
def createAttendsTo(data:dict, **kwargs):
    return crudReturn(AttendsTo(**data).insert())

@router.route('/attendsTo/<int:idAp>/<int:idPa>', methods=['PUT', 'PATCH'])
@requiresRole(['administrative'])
@passJsonData
@appointmentExists(AttendsTo, ['idAp', 'idPa'], ['idAp', 'idPa'])
@passJsonData
def updateAttendsTo(obj:AttendsTo, data:dict, **kwargs):
    data.pop('idAp', None)
    data.pop('idPa', None)
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
@appointmentExists(AttendsTo, ['idAp', 'idPa'], ['idAp', 'idPa'])
def deleteAttendsTo(obj:AttendsTo, **kwargs):
    return crudReturn(obj.delete())

# # -- DATA INPUTTED WHEN A PATIENT IS BEING INTERVIEWED IN AN APPOINTMENT

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

    statementData = f"""SELECT appointment.* FROM {', '.join(tables)}
                        {' WHERE ' + ' AND '.join(conditions) if len(conditions) > 0 else ''}
                        LIMIT {limit} OFFSET {offset}"""

    statementCount = f"""SELECT COUNT(appointment.id) FROM {', '.join(tables)}
                        {' WHERE ' + ' AND '.join(conditions) if len(conditions) > 0 else ''}"""

    resultData = [{'appointment': asdict(Appointment(*ap))} for ap in db.execute(statementData, values).fetchall()]

    resultCount = db.execute(statementCount, values).fetchone()[0]
    
    for r in resultData:
        doc = Doctor.getDocOfAp(r['appointment']['id'])
        br = Branch.getBranchOfAp(r['appointment']['id'])

        if isinstance(doc, User):
            r['doctor'] = userToReturn(doc, id, **kwargs)
        else:
            r['doctor'] = {}

        if isinstance(br, Branch):
            r['branch'] = asdict(br)
        else:
            r['branch'] = {}

        if _typeFilter == 'mine':
            imAttending = AttendsTo.selectOne({'idAp': r['appointment']['id'], 'idPa': _id})
            r['imAttending'] = isinstance(imAttending, AttendsTo) # indicates whether the patient is already scheduled for this appointment or not

    return crudReturn(resultData, {'total': resultCount})
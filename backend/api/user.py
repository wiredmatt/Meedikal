from flask import Blueprint, request
from dataclasses import asdict

from util.crud import crudReturn
from util.requestParsers import parseRole
from middleware.authGuard import requiresAuth
from middleware.data import passJsonData

from models.Specialty import *
from models.User import *

router = Blueprint('user', __name__, url_prefix='/user')

def userToReturn(user: User, role=None):
    if user is None:
        return None
    if role is None:
        role = parseRole(request)
    
    obj = {'user': asdict(user), 
           'roles': User.getRoles(ci=user.ci),
           'phoneNumbers': [asdict(p) for p in UserPhone.getByCi(user.ci)]}

    if role == 'medicalPersonnel' or role == 'doctor' or role == 'medicalAssitant':
        hasSpec = MpHasSpec.filter({'ciMp': user.ci})
        obj['specialties'] = [asdict(hsp) for hsp in hasSpec]

        for hsp in obj['specialties']:
            hsp['title'] = Specialty.getById(hsp['idSpec']).title

    obj['user'].pop('password', None)
    
    return obj

@router.route('/all', methods=['GET', 'POST']) # GET | POST /api/user/all
@passJsonData
def allUsers(data:dict=None):
    users = User.filter(data)
    return crudReturn(users)

@router.get('/<int:ci>') # GET /api/user/<ci>
@router.post('/ci') # POST /api/user/ci
@passJsonData
def getUserByCi(ci:int=None, data:dict=None):
    if request.method == 'POST':
        ci = data['ci']

    return crudReturn(userToReturn(User.getByCi(ci)))

@router.post('') # POST /api/user
@passJsonData
def createUser(data:dict):
    return crudReturn(userToReturn(User(**data).save(data)))

@router.route('', methods=['PUT', 'PATCH']) # PUT | PATCH /api/user
@passJsonData
def updateUser(data:dict):
    return crudReturn(User.update(data))

@router.delete('') # DELETE /api/user
@passJsonData
def deleteUser(data:dict):
    return crudReturn(User.delete(data))

@router.route('/patient', methods=['POST', 'DELETE']) # POST | DELETE /api/patient
@passJsonData
def patient(data:dict):
    if request.method == 'POST':
        result = userToReturn(Patient(**data).save(data))
    else:
        result = Patient.delete(data)

    return crudReturn(result)

@router.route('/medicalPersonnel', methods=['POST', 'DELETE']) # POST | DELETE /api/medicalPersonnel
@passJsonData
def medicalPersonnel(data:dict):
    if request.method == 'POST':
        result = userToReturn(MedicalPersonnel(**data).save(data))
    else:
        result = MedicalPersonnel.delete(data)

    return crudReturn(result)

@router.route('/doctor', methods=['POST', 'DELETE']) # POST | DELETE /api/doctor
@passJsonData
def doctor(data:dict):
    if request.method == 'POST':
        result = userToReturn(Doctor(**data).save(data))
    else:
        result = Doctor.delete(data)

    return crudReturn(result)

@router.route('/medicalAssistant', methods=['POST', 'DELETE']) # POST | DELETE /api/medicalAssistant
@passJsonData
def medicalAssitant(data:dict):
    if request.method == 'POST':
        result = userToReturn(MedicalAssitant(**data).save(data))
    else:
        result = MedicalAssitant.delete(data)

    return crudReturn(result)

@router.route('/administrative', methods=['POST', 'DELETE']) # POST | DELETE /api/administrative
@passJsonData
def administrative(data:dict):
    if request.method == 'POST':
        result = userToReturn(Administrative(**data).save(data))
    else:
        result = Administrative.delete(data)

    return crudReturn(result)

@router.post('/surname1') # POST /api/user/surname1 filter by surname1 and role
@router.get('/<surname1>') # GET /api/user/<surname1> filter only by surname1
@passJsonData
def userBySurname1(surname1:str=None, data:dict=None):
    if request.method == 'POST':
        result = User.filter(data)
    else:
        result = User.filter({'surname1' : surname1})

    return crudReturn([userToReturn(u) for u in result])

@router.post('/name1surname1') # GET /api/user/name1surname1
@router.get('/<name1>/<surname1>') # GET /api/user/<name1>/<surname1>
@passJsonData
def userByName1nSurname1(name1:str=None,surname1:str=None, data:dict=None):
    if request.method == 'POST':
        result = User.filter(data)
    else:
        result = User.filter({'name1' : name1, 'surname1' : surname1})

    return crudReturn([userToReturn(u) for u in result])

@router.route('/phoneNumbers', methods=['POST', 'DELETE'])
@router.get('/phoneNumbers/<ci>')
@passJsonData
def phoneNumbers(ci:int=None, data:dict=None):
    result = None

    if request.method == 'GET':
        result = UserPhone.getByCi(ci)
    else:
        data = data['userPhone']
        for phone in data:
            if request.method == 'POST':
                UserPhone(**phone).saveOrGet(phone)
            elif request.method == 'DELETE':
                rows = UserPhone.delete(phone)
        result = data if request.method == 'POST' else rows

    return crudReturn(result)

@router.route('/medicalPersonnel/mpHasSpec', methods=['POST', 'DELETE'])
@router.get('/medicalPersonnel/mpHasSpec/<int:ciMp>')
@passJsonData
def mpHasSpec(ciMp:int=None, data:dict=None):
    if request.method == 'GET':
        result = MpHasSpec.filter({'ciMp': ciMp})
        for sp in result:
            sp['title'] = Specialty.getById(sp['idSpec']).title
    else:
        data = data['mpHasSpec']
        result = []
        for hsp in data:
            if request.method == 'POST':
                if hsp.get('idSpec', None) is None:
                    _sp = Specialty(**hsp).saveOrGet({'title': hsp['title']})
                    hsp['idSpec'] = _sp.id
                    hsp.pop('title')
                
                hspInstance = MpHasSpec(**hsp).save(hsp)
                hspReturn = asdict(hspInstance)
                hspReturn['title'] = Specialty.getById(hsp['idSpec']).title
                result.append(hspReturn)

            elif request.method == 'DELETE':
                result = MpHasSpec.delete(hsp)

    return crudReturn(result)

@router.post('/medicalPersonnel/specialty') # {'title': 'oftalmology', 'extraFilters': {'role': 'doctor'}}
@router.get('/medicalPersonnel/<title>') # specialty title
@passJsonData
def getMpUsersBySpecialty(title:str=None, data:dict=None):
    users = []
    if request.method == 'POST':
        mps: list[MedicalPersonnel] = MedicalPersonnel.filter(data)
    else:
        specialty = Specialty.filter({'title': title}, returns='one')
        if specialty is not None:
            mps: list[MedicalPersonnel] = MedicalPersonnel.filter({'specialty.id': specialty.id,
                                             'mpHasSpec.ciMp': {
                                                 'value': 'medicalPersonnel.ci',
                                                 'joins': True},
                                             'mpHasSpec.idSpec': {
                                                 'value': 'specialty.id',
                                                 'joins': True}})
        else: # specialty doesn't exist
            return crudReturn([])
    
    users = [User.getByCi(mp.ci) for mp in mps]
            
    return crudReturn([userToReturn(u, 'medicalPersonnel') for u in users])
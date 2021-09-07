from dataclasses import asdict

from flask import json, Blueprint, request

from models.Specialty import *
from models.User import *
from util.returnMessages import *

router = Blueprint('user', __name__, url_prefix='/user')

def getTypes(ci):
    types = [User.__tablename__]

    if Administrative.getByCi(ci) is not None:
        types.append(Administrative.__tablename__)
    
    if Patient.query.filter(Patient.ci==ci).one_or_none() is not None:
        types.append(Patient.__tablename__)
    
    if MedicalPersonnel.query.filter(MedicalPersonnel.ci==ci).one_or_none() is not None:
        types.append(MedicalPersonnel.__tablename__)
    
        if Doctor.query.filter(Doctor.ci==ci).one_or_none() is not None:
            types.append(Doctor.__tablename__)
        
        elif MedicalAssitant.query.filter(MedicalAssitant.ci==ci).one_or_none() is not None:
            types.append(MedicalAssitant.__tablename__)
    
    return types

def filterByType(userType=None, request=None) -> Query:
    if request is not None:
        userType = json.loads(request.data)['user'].get('userType', None)
    if userType == None:
        return User.query
    elif userType == 'patient':
        return User.query.filter(User.ci == Patient.ci)
    elif userType == 'medicalPersonnel':
        return User.query.filter(User.ci == MedicalPersonnel.ci)
    elif userType == 'doctor':
        return User.query.filter(User.ci == Doctor.ci)
    elif userType == 'medicalAssistant':
        return User.query.filter(User.ci == MedicalAssitant.ci)
    elif userType == 'administrative':
        return User.query.filter(User.ci == Administrative.ci)

def userToReturn(user: User, userType=None, relationType=None):
    if user is None:
        return None

    obj = {'user': asdict(user), 
           'phoneNumbers': [asdict(p) for p in UserPhone.query.filter(
                                    UserPhone.ci == user.ci).all()],
           'relatives': [asdict(r) for r in UIsRelatedTo.query.filter(
                                    UIsRelatedTo.user1==user.ci).all()],
            'types': getTypes(user.ci)}

    if userType == 'medicalPersonnel' or userType == 'doctor' or userType == 'medicalAssitant':
        obj['specialties'] = [asdict(sp) for sp in Specialty.query.filter(and_(
                                        MpHasSpec.ciMp == user.ci,
                                        MpHasSpec.idSpec == Specialty.id)).all()]

    if relationType is not None:
        obj['relationType'] = relationType

    obj['user'].pop('password', None)

    return obj

@router.get('/all') # GET /api/user/all
def allUsers():
    users = filterByType(request=request).all()
    return crudv2(request=request, preparedResult=[userToReturn(u) for u in users])

@router.get('') # GET /api/user
def user():
    data = json.loads(request.data)
    
    if data.get('password', None) is not None: # encrypt the password
        data['password'] = generate_password_hash(data['password'])

    request.data = json.dumps({User.__tablename__: data})
    return crudv2(User,request)
    
@router.delete('') # DELETE /api/user
def deleteUser(): # logicalCD (logical Create / Delete) = set active to False or True (0,1)
    data = json.loads(request.data)['user']
    user = filterByType(request=request).filter(User.ci == data['ci']).one_or_none()
    if data.get('logicalCD', None) is not None:
        if user is not None:
            user.active = data['logicalCD']
            user.update()
            return crudv2(request=request,preparedResult=userToReturn(user))
    else:
        return crudv2(User,request)

@router.get('/surname1') # GET /api/user/surname1
def userBySurname1():
    data = json.loads(request.data)['user']
    users = filterByType(request=request).filter(User.surname1 == data['surname1']).all()
    return crudv2(User, preparedResult=[userToReturn(u) for u in users], jsonReturn=True)

@router.get('/name1surname1') # GET /api/user/name1surname1
def userByName1nSurname1():
    data = json.loads(request.data)['user']
    users = filterByType(request=request).filter(and_(
                                            User.surname1 == data['surname1'],
                                            User.name1 == data['name1'])).all()

    return crudv2(User, preparedResult=[userToReturn(u) for u in users], jsonReturn=True)

@router.route('', methods=['POST', 'PUT', 'PATCH']) # POST | PUT | PATCH /api/user
def create_or_update():
    return crudv2(User, request)

@router.route('/patient', methods=['POST', 'DELETE']) # create or delete patient table
def patient():
    return crudv2(Patient, request)

@router.route('/medicalPersonnel', methods=['POST', 'DELETE']) # create or delete medicalPersonnel | doctor | medicalassistant user
def medicalPersonnel():
    return crudv2(MedicalPersonnel,request)

@router.route('/doctor', methods=['POST', 'DELETE']) # create or delete medicalPersonnel | doctor | medicalassistant user
def doctor():
    return crudv2(Doctor,request)

@router.route('/medicalAssistant', methods=['POST', 'DELETE']) # create or delete medicalPersonnel | doctor | medicalassistant user
def medicalAssistant():
    return crudv2(MedicalAssitant,request)

@router.route('/phoneNumbers', methods=['POST', 'DELETE', 'GET'])
def phoneNumbers():
    return crudv2(UserPhone,request)

@router.route('/relatives', methods=['POST', 'PATCH', 'DELETE'])
def relatives():
    return crudv2(UIsRelatedTo,request)

@router.get('/relatives')
def getRelatives():
    _relatives = UIsRelatedTo.query.filter(UIsRelatedTo.user1 == json.loads(request.data)['user']['ci']).all()
    #               user1 is <relationType> of user2
    __relatives = [userToReturn(user, 
                    relationType = next(r.relationType for r in _relatives
                                        if r.user2 == user.ci))
                    for user in 
                    [User.query.filter(User.ci==r.user2).first()
                     for r in _relatives]]

    return crudv2(request=request, preparedResult=__relatives)

@router.route('/medicalPersonnel/mpHasSpec', methods=['POST','GET', 'DELETE'])
def specialties(): #1 create / get specialties first, then add to MpHasSpec
    if request.method == 'POST':
        data = json.loads(request.data)
        mpHasSpec = data['mpHasSpec']

        _specialties = [getOrCreate(Specialty, Specialty(title=sp['title']),
                        f"title = '{sp['title']}'") for sp in mpHasSpec]

        for sp in _specialties:
                for _mpSpec in mpHasSpec:
                    if _mpSpec['title'] == sp[0][0].title:
                        _mpSpec['idSpec'] = sp[0][0].id
                    _mpSpec.pop('title', None)

        request.data = json.dumps({MpHasSpec.__tablename__: mpHasSpec})
    
    return crudv2(MpHasSpec,request)

@router.get('/medicalPersonnel/specialties') # get specialties of mp user
def getSpecialtiesOfMp():
    _specialties = MpHasSpec.query.filter(MpHasSpec.ciMp == json.loads(request.data)['user']['ci']).all()

    __specialties = [asdict(Specialty.query.filter(Specialty.id == sp.idSpec).first())
                    for sp in _specialties]

    return crudv2(request=request,preparedResult=__specialties)

@router.get('/medicalPersonnel/specialty') # GET /api/user/medicalPersonnel/specialty get medicalpersonnel users by specialty
def getMedicalPersonnelBySpecialty():
    data = json.loads(request.data)

    specialty = Specialty.query.filter(Specialty.title == data['specialty']).one_or_none()

    if specialty is None:
        return recordDoesntExist(Specialty.__tablename__)
    else:
        specialtyId = specialty.id

    users = filterByType(data['user']['userType']).filter(and_(
                                            MpHasSpec.idSpec == specialtyId,
                                            MpHasSpec.ciMp == User.ci 
                                            )).all()

    return crudv2(request=request, preparedResult=[userToReturn(u, userType=data['user']['userType']) for u in users])
from flask import Blueprint, request
from dataclasses import asdict
from functools import wraps
from werkzeug.datastructures import FileStorage
from util.crud import crudReturn
from util.requestParsers import parseRole
from middleware.authGuard import getCurrentRole, requiresAuth, requiresRole
from middleware.data import passJsonData, passFile, paginated, resourceExists
from models.Specialty import *
from models.User import *

router = Blueprint('users', __name__, url_prefix='/users')

def userExists(Model:BaseModel=User, idFields=['id'], idArgs=['idUser'], abort=True):
    def decorator(f):
        @resourceExists(Model, idFields, idArgs, abort)
        @wraps(f)
        def wrapper(obj, *args,**kwargs):
            return f(*args, **kwargs, user=obj)
        
        return wrapper
    return decorator

def userToReturn(user: User, id:int=0, currentRole:str='', role=None, **kwargs):
    if not User:
        return None
    if not role:
        role = parseRole(request)

    _user = asdict(user)

    phones = []

    if user.id == id or currentRole == 'administrative':
        phones = UserPhone.selectMany({'id': user.id})
    else:
        _user.pop('email', None)
        _user.pop('location', None)

    obj = {'user': _user, 
           'roles': User.getRoles(user.id),
           'phoneNumbers': phones}

    if role == 'doctor':
        hasSpec = DocHasSpec.selectMany({'idDoc': id})

        if len(hasSpec) > 0:
            obj['specialties'] = [Specialty.selectOne({'id': sp.idSpec}).title for sp in hasSpec]

    obj['user'].pop('password', None)

    return obj

@router.route('/all', methods=['GET', 'POST'])
@getCurrentRole
@paginated()
def allUsers(offset:int, limit: int, data:dict={}, **kwargs):
    return crudReturn([userToReturn(u, **kwargs) for u in User.selectMany(dict(data or {}).copy(), offset=offset, limit=limit)])

@router.get('/<int:idUser>')
@getCurrentRole
def getUserById(idUser:int=None, **kwargs):
    return crudReturn(userToReturn(User.selectOne({'id': idUser}), **kwargs))

@router.post('')
@requiresRole(['administrative'])
@getCurrentRole
@passJsonData
def createUser(data:dict, **kwargs):
    return crudReturn(userToReturn(User(**data).insert(), **kwargs))

@router.route('/<int:idUser>', methods=['PUT', 'PATCH'])
@requiresRole(['administrative', 'self'])
@passJsonData
@userExists()
def updateUser(user:User, data:dict, **kwargs):
    return crudReturn(userToReturn(user.update(data), **kwargs))

@router.delete('/<int:idUser>')
@requiresRole(['administrative'])
@userExists()
def deleteUser(user:User, **kwargs):
    return crudReturn(user.delete())

@router.route('/updatePhoto/<int:idUser>', methods=['POST', 'PUT', 'PATCH'])
@requiresRole(['administrative', 'self'])
@passFile(['jpg', 'jpeg', 'png'])
@userExists()
def updatePhoto(user:User, file:FileStorage, **kwargs):
    return crudReturn(userToReturn(user.updatePhoto(file), **kwargs))

@router.route('/patients/<int:idUser>', methods=['POST', 'DELETE'])
@requiresRole(['administrative'])
@userExists()
def patient(user:User, **kwargs):
    if request.method == 'POST':
        Patient(user.id).insertOrSelect()
        result = userToReturn(user, **kwargs)
    else:
        result = Patient.selectOne({'id': user.id}).delete()

    return crudReturn(result)

@router.route('/doctors/<int:idUser>', methods=['POST', 'DELETE'])
@requiresRole(['administrative'])
@userExists()
def doctor(user:User, **kwargs):
    if request.method == 'POST':
        Doctor(user.id).insertOrSelect()
        result = userToReturn(user, role='doctor', **kwargs)
    else:
        result = Doctor.selectOne({'id': user.id}).delete()

    return crudReturn(result)

@router.route('/administratives/<int:idUser>', methods=['POST', 'DELETE'])
@requiresRole(['administrative'])
@userExists()
def administrative(user:User, **kwargs):
    if request.method == 'POST':
        Administrative(user.id).insertOrSelect()
        result = userToReturn(user, **kwargs)
    else:
        result = Administrative.selectOne({'id': user.id}).delete()

    return crudReturn(result)

@router.route('/<surname1>', methods=['GET', 'POST'])
@getCurrentRole
@paginated()
def userBySurname1(offset:int, limit: int, surname1:str, **kwargs):
    result = User.select({'surname1' : surname1}, offset=offset, limit=limit)
    return crudReturn([userToReturn(u, **kwargs) for u in result])

@router.route('/<name1>/<surname1>', methods=['GET', 'POST'])
@getCurrentRole
@paginated()
def userByName1nSurname1(offset:int, limit: int, name1:str=None, surname1:str=None, **kwargs):
    result = User.select({'name1' : name1, 'surname1' : surname1}, offset=offset, limit=limit)
    return crudReturn([userToReturn(u, **kwargs) for u in result])

@router.route('/phoneNumbers/<int:idUser>', methods=['GET', 'POST', 'DELETE'])
@passJsonData
@requiresRole(['administrative', 'self'])
@userExists()
def phoneNumbers(user:User, data:dict=None, **kw):
    result = None

    if request.method == 'GET':
        result = UserPhone.selectMany({'id': user.id})
    elif request.method == 'POST':
        result = UserPhone(**data).insert()
    else:
        result = UserPhone.selectOne(data).delete()

    return crudReturn(result)

@router.get('/doctors/specialties/<int:idDoc>')
@requiresAuth
def getSpOfDoc(idDoc:int, **kwargs):
    result = DocHasSpec.selectMany({'idDoc': idDoc})
    if len(result) > 0:
        result = [asdict(hsp) for hsp in result]

        for sp in result:
            sp['title'] = Specialty.selectOne({'id': sp['idSpec']}).title
    return crudReturn(result)

@router.route('/doctors/specialties/<int:idDoc>/<string:title>', methods=['POST', 'DELETE'])
@requiresRole(['administrative'])
def addOrDeleteDocsSpec(idDoc:int, title:str=None):
    if request.method == 'POST':
        _sp: Specialty = Specialty(title=title).insertOrSelect()
        result = asdict(DocHasSpec(_sp.id, idDoc).insert())
        result['title'] = title
    else:
        _sp = Specialty.selectOne({title: title})
        result = DocHasSpec.selectOne({'idSpec' : _sp.id, 'idDoc': idDoc}).delete()

    return crudReturn(result)
 
@router.route('/doctors/<string:specialty>', methods=['GET', 'POST'])
@requiresAuth
@paginated()
def filterDocsBySpecialty(offset:int, limit: int, specialty:str, **kwargs):
    _doctors = []

    sp = Specialty.selectOne({'title': specialty})
    
    if sp:
        hsps = DocHasSpec.selectMany({'idSpec': sp.id}, offset=offset, limit=limit)

        if len(hsps) > 0:
            for hsp in hsps:
                _doctors.append(userToReturn(User.selectOne({'id': hsp.idDoc}), **kwargs)) 

    return crudReturn(_doctors)
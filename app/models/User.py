import os
from dateutil.parser.isoparser import isoparse
from werkzeug.datastructures import FileStorage
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from util.errors import UpdatePasswordError, InactiveUserError
from dataclasses import dataclass
from ._base import BaseModel, db

from datetime import datetime, timedelta
from typing import Optional

from config import Config
import jwt

@dataclass
class User(BaseModel):
    __tablename__ = 'user'
    
    id:int
    name1:str
    surname1:str
    sex:str
    birthdate:str
    location:str
    email:str
    password:str
    name2:Optional[str] = None
    surname2:Optional[str] = None
    genre:Optional[str] = None
    active:Optional[bool] = True
    photoUrl:Optional[str] = None

    def __init__(self, id:int, name1:str, surname1:str, sex:str, birthdate:datetime, location:str, email:str, password:str, name2:str=None, surname2:str=None, genre:str=None, active:bool=None, photoUrl:str=None):
        self.id = id
        self.name1 = name1
        self.surname1 = surname1
        self.sex = sex

        try:
            isoparse(birthdate)
            self.birthdate = birthdate
        except:
            self.birthdate = None

        self.location = location
        self.email = email
        self.password = password
        self.name2 = name2
        self.surname2 = surname2
        self.genre = genre
        self.active = active
        self.photoUrl = photoUrl or '/images/user-placeholder.png'
        
    @classmethod
    def parseItems(cls, items: dict):
        try:
            extraFilters:dict = items.get('extraFilters', None)
            if extraFilters is not None:
                userType = extraFilters.get('role', None)
                items[f'{userType}.id'] = {'value': 'user.id', 'joins': True}
            
            items.pop('extraFilters', None)
            items.pop('password', None) # doesn't make sense to filter by password
        except:
            pass
        
        return items

    @classmethod
    def select(cls, items: dict={}, operator:str = 'AND', shape='list', offset:int=None, limit:int=None):
        items = cls.parseItems(items)
        return super().select(items, operator, offset, limit, shape)

    @classmethod
    def selectOne(cls, items: dict={}, operator:str = 'AND'):
        items = cls.parseItems(items)
        return super().selectOne(items, operator)
    
    @classmethod
    def selectMany(cls, items: dict={}, operator:str = 'AND', offset:int=None, limit:int=None):
        items = cls.parseItems(items)
        return super().selectMany(items, operator, offset, limit)

    @classmethod
    def count(cls, items: dict={}, operator:str = 'AND'):
        items = cls.parseItems(items)
        return super().count(items, operator)
    
    def insert(self) -> 'User':
        try:
            self.password = generate_password_hash(self.password)
        except:
            if self.id:
                self.password = generate_password_hash(self.id)

        return super().insert()

    def update(self, data: dict={}):
        if data.get('password', None) is not None:
            raise UpdatePasswordError()

        birthdate = data.get('birthdate', None)

        if birthdate is not None:
            data['birthdate'] = isoparse(birthdate)
        
        return super().update(data)

    @classmethod
    def getRoles(cls, id:int) -> list[str]:
        roles = []

        if Administrative.select({'id': id}, shape='one') is not None:
            roles.append(Administrative.__tablename__)

        if Patient.select({'id': id}, shape='one') is not None:
            roles.append(Patient.__tablename__)
        
        if Doctor.select({'id': id}, shape='one') is not None:
            roles.append(Doctor.__tablename__)
                
        return roles

    def updatePassword(self, password:str):
        password = generate_password_hash(password)
        
        statement = f"""UPDATE {self.__tablename__} SET password = ? WHERE id = ?"""
        cursor = db.cursor()
        cursor.execute(statement, [password, self.id])
        db.commit()

        self.password = password

        return self

    def updatePhoto(self, file: FileStorage) -> 'User':
        file.filename = secure_filename(f'{self.id}.jpg') # force jpg format
        photoUrl = os.path.join(Config.UPLOAD_FOLDER, file.filename)

        file.save(photoUrl)
        
        self.update({'photoUrl': photoUrl})

        return self

class AuthUser:

    @classmethod
    def login(cls, id:int, password:str):
        user: User = User.select({'id': id}, shape='one')
        if not user.active:
            raise InactiveUserError

        try:
            if check_password_hash(user.password, password):
                now = datetime.utcnow() 
                payload = { # expires in 365 days.
                    'exp': now + timedelta(days=365),
                    'iat': now,
                    'sub': id
                }
                token = jwt.encode(payload,Config.SECRET_KEY, algorithm="HS256")
                return token
            else:
                return None
        except: # incorrect id or password
            return None

    @staticmethod
    def verifyToken(token) -> int: # exceptions handled by auth error handler.
        payload = jwt.decode(token, Config.SECRET_KEY, algorithms=["HS256"])
        return payload['sub']

@dataclass # since phone is a multivalued attribute, it has its own table.
class UserPhone(BaseModel):
    __tablename__ = 'userPhone'

    id: int
    phone: str # since phone numbers aren't real numbers it's better to store them as strings. Some countries (like Uruguay), start their cellphone numbers with a 0, which on input would be ignored by the DBMS if the datatype was Integer. 

@dataclass
class Patient(BaseModel):
    __tablename__ = 'patient'
    id: int

@dataclass # users from the medical personnel, who are doctors. 
class Doctor(BaseModel):
    __tablename__ = 'doctor'
    id: int

    @classmethod
    def getBySpecialty(cls, title:str, offset:int, limit:int, data:dict={}, returns:str='all'):
        
        filters = [f'{k} = ?' for k in data.keys()]
        values = [title] + [v for v in data.values()]

        statement = f"""
                SELECT user.* 
                FROM doctor, user, docHasSpec, specialty
                WHERE doctor.id = docHasSpec.idDoc
                AND doctor.id == {User.__tablename__}.id
                AND docHasSpec.idSpec = specialty.id
                AND specialty.title = ?
                {'AND '.join(filters)}
                LIMIT {limit} OFFSET {offset}
                """
                
        if returns == 'all':
            return [User(*obj) for obj in db.execute(statement, values).fetchall()]
        else:
            try:
                return User(*db.execute(statement, [title]).fetchone())
            except:
                return None
    
    @classmethod
    def getDocOfAp(cls, idAp:int):
        statement = f"""
        SELECT user.* FROM user, assignedTo WHERE
        assignedTo.idAp = ? AND assignedTo.idDoc = user.id
        """

        result = db.execute(statement, [idAp]).fetchone()

        if result:
            return User(*result)
        else:
            return {}
@dataclass
class Administrative(BaseModel):
    __tablename__ = 'administrative'
    id: int
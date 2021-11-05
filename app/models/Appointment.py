from datetime import datetime, timedelta
from ._base import BaseModel, db
from .User import Patient
from dataclasses import asdict, dataclass
from dateutil.parser import isoparse

from typing import Optional

DATE_TIME_STRING_FORMAT = '%Y-%m-%dT%H:%M:%S.%fZ'

@dataclass
class Appointment(BaseModel):
    __tablename__ = 'appointment'

    id:int
    name:str
    date:str

    startsAt:Optional[str] = None
    endsAt:Optional[str] = None
    etpp:Optional[int] = None # estimated time per patient, in minutes
    maxTurns:Optional[int] = None # max patients to be attended

    def __init__(self, id:int=None, name:str=None,date:str=None, startsAt:str=None, endsAt:str=None, etpp:int=None, maxTurns:int=None):
        self.id = id
        self.name = name
        
        try:
            isoparse(date)
            self.date = date
        except:
            self.date = None
        
        try:
            isoparse(startsAt)
            self.startsAt = startsAt
        except:
            self.startsAt = None

        try:
            isoparse(endsAt)
            self.endsAt = endsAt
        except:
            self.endsAt = None
            
        self.etpp = etpp
        self.maxTurns = maxTurns

    def insert(self, commit=True):
        data = asdict(self)
        try:
            if data.get('startsAt', None) is not None and data.get('endsAt', None) is not None:
                startsAt = datetime.strptime(data['startsAt'], DATE_TIME_STRING_FORMAT)
                endsAt = datetime.strptime(data['endsAt'], DATE_TIME_STRING_FORMAT)

                diff = endsAt - startsAt
                diffMins = diff.total_seconds() / 60
                
                if diffMins < 10:
                    raise 'time interval too short.'

                etpp = data.get('etpp', None)

                maxTurns = data.get('maxTurns', None)
                
                if etpp is None and maxTurns is None:
                    etpp = 10
                    maxTurns = int(diffMins // etpp) # floor
                elif etpp is None:
                    etpp = int(diffMins // maxTurns) # floor
                elif maxTurns is None:
                    maxTurns = int(diffMins // etpp) # floor
                
                if diffMins // maxTurns < 1.0: # less than a minute per patient
                    raise 'number of turns too high for the chosen time interval.'
                elif diffMins // etpp < 1.0: # less than 1 turn
                    raise 'etpp too high for the chosen time interval.'

                data['maxTurns'] = maxTurns
                data['etpp'] = etpp

                result = super().insert(data, commit)

                FreeTurns.generateTurns(maxTurns, result.id)
                FreeTimes.generateTimes(startsAt, endsAt, etpp, result.id)

                return result
            else: 
                raise 'no times provided'
        except Exception as exc:
                _exc = str(exc)

                if 'short' in _exc:
                    data['startsAt'] = None
                    data['endsAt'] = None
                elif 'turns' in _exc:
                    data['maxTurns'] = None
                elif 'etpp' in _exc:
                    data['etpp'] = None
                else: # invalid datetimes
                    data['startsAt'] = None
                    data['endsAt'] = None

                result = super().insert(commit)

                if maxTurns is not None:
                    FreeTurns.generateTurns(maxTurns, result.id)

                return result

@dataclass
class AssignedTo(BaseModel): # Doctor < assignedTo > Appointment
    __tablename__ = 'assignedTo'
    __idField__ = 'idAp,idDoc'
    __compoundIdField__ = True

    idAp: int
    idDoc: int
    
@dataclass
class AttendsTo(BaseModel): # Patient < attendsTo > [ Doctor < assignedTo > Appointment]
    __tablename__ = 'attendsTo'
    __idField__ = 'idAp,idPa'
    __compoundIdField__ = True

    idAp: int
    idPa: int

    motive: Optional[str] = None
    time: Optional[str] = None
    number: Optional[int] = None
    notes: Optional[str] = None

    def __init__(self,idAp:int,idPa:int,motive:str=None,time:str=None, number:int=None, notes:str=None):
        self.idAp = idAp
        self.idPa = idPa
        self.motive = motive
        self.notes = notes
              
        try:
            isoparse(time)
            self.time = time
        except:
            self.time = None
            
        self.number = number

    @classmethod
    def getPatients(cls, idAp) -> list[Patient]:
        statement = f"""
        SELECT idPa from attendsTo
        WHERE idAp = ?
        """

        result = db.execute(statement, [idAp]).fetchall()

        if result:
            return [Patient(*p) for p in result]
        else:
            return []

@dataclass
class FreeTurns(BaseModel):
    __tablename__ = 'freeTurns'
    __idField__ = 'idAp,value'
    __compoundIdField__ = True

    idAp: int
    value: int

    @classmethod
    def generateTurns(cls, maxTurns:int, idAp:int) -> bool:
        _turns = list(range(1, maxTurns + 1))
        turns = []
        for turn in _turns:
            turns.append((idAp, turn))

        statement = f"""
        INSERT INTO freeTurns (idAp, value) VALUES (?, ?)
        """
        try:
            db.cursor().executemany(statement, turns)

            db.commit()

            return True
        except Exception:
            return False

@dataclass
class FreeTimes(BaseModel):
    __tablename__ = 'freeTimes'
    __idField__ = 'idAp,value'
    __compoundIdField__ = False

    idAp: int
    value: int

    @classmethod 
    def generateTimes(cls, startsAt:datetime, endsAt:datetime, etpp:int, idAp:int):
        datetimes = [(idAp, startsAt.strftime(DATE_TIME_STRING_FORMAT))]

        _startsAt = startsAt

        while _startsAt + timedelta(minutes=etpp) < endsAt:
            _startsAt += timedelta(minutes=etpp)
            datetimes.append((idAp, _startsAt.strftime(DATE_TIME_STRING_FORMAT)))

        statement = f"""
        INSERT INTO freeTimes (idAp, value) VALUES (?, ?)
        """

        try:
            db.cursor().executemany(statement, datetimes)

            db.commit()

            return True
        except:
            return False    

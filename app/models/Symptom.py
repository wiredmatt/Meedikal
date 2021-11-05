from ._base import BaseModel
from dataclasses import dataclass
from typing import Optional

@dataclass
class Symptom(BaseModel):
    __tablename__ = 'symptom'

    id:int
    name:str
    description:Optional[str] = None

    def __init__(self, id:int=None, name:str=None, description:str=None):
        self.id = id
        self.name = name
        self.description = description

@dataclass
class RegistersSy(BaseModel): # { Patient < attendsTo > [ Doctor < assignedTo > Appointment] } < registersSy > Symptom
    __tablename__ = 'registersSy'
    __idField__ = 'idAp,idPa,idSy'
    __compoundIdField__ = True

    idAp:int
    idPa:int
    idSy:int
    detail:Optional[str] = None
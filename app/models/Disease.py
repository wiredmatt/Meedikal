from ._base import BaseModel
from dataclasses import dataclass
from typing import Optional

@dataclass
class Disease(BaseModel):
    __tablename__ = 'disease'

    id:int
    name:str
    description:Optional[str]

    def __init__(self, id:int=None, name:str=None, description:str=None):
        self.id = id
        self.name = name
        self.description = description

@dataclass
class Diagnoses(BaseModel): # { Patient < attendsTo > [ Doctor < assignedTo > Appointment] } < diagnoses > Disease
    __tablename__ = 'diagnoses'
    __idField__ = 'idAp,idPa,idDis'
    __compoundIdField__ = True
    
    idAp: int
    idPa: int
    idDis: int
    detail: Optional[str] = None
from ._base import BaseModel
from dataclasses import dataclass
from typing import Optional

@dataclass
class ClinicalSign(BaseModel):
    __tablename__ = 'clinicalSign'

    id:int
    name:str
    description:Optional[str] = None
    
    def __init__(self, id:int=None, name:str=None, description:str=None):
        self.id = id
        self.name = name
        self.description = description

@dataclass
class RegistersCs(BaseModel): # { Patient < attendsTo > [ Doctor < assignedTo > Appointment] } < registersCs > ClinicalSign
    __tablename__ = 'registersCs'
    __idField__ = 'idAp,idPa,idCs'
    __compoundIdField__ = True
    
    idAp: int
    idPa: int
    idCs: int
    detail: Optional[str] = None
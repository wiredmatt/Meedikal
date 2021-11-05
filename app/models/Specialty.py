from ._base import BaseModel
from dataclasses import dataclass
from typing import Optional

@dataclass
class Specialty(BaseModel):
    __tablename__ = 'specialty'

    id:int
    title:str

    def __init__(self,id:int=None,title:str=None):
        self.id = id
        self.title = title

@dataclass
class DocHasSpec(BaseModel): 
    __tablename__ = 'docHasSpec'
    __idField__ = 'idSpec,idDoc'
    __compoundIdField__ = True

    idSpec:int
    idDoc:int

    detail:Optional[str] = None

    def __init__(self,idSpec,idDoc):
        self.idSpec = idSpec
        self.idDoc = idDoc
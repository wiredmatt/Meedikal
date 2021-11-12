from ._base import BaseModel, db
from dataclasses import dataclass

@dataclass
class Branch(BaseModel):
    __tablename__ = 'branch'

    id:int
    name:str
    phoneNumber:str
    location:str
    googleMapsSrc:str

    def __init__(self, id:int=None, name:str=None, phoneNumber:str=None, location:str=None, googleMapsSrc:str=None):
       self.id = id
       self.name = name
       self.phoneNumber = phoneNumber
       self.location = location
       self.googleMapsSrc = googleMapsSrc

    @classmethod
    def getBranchOfAp(cls, idAp):
        statement = f"""
        SELECT branch.* FROM branch, apTakesPlace
        WHERE apTakesPlace.idAp = ? AND apTakesPlace.idBranch = branch.id
        """

        result = db.execute(statement,[idAp]).fetchone()

        try:
            return cls(*result)
        except:
            return None

@dataclass
class ApTakesPlace(BaseModel): # Appointment < apTakesPlace > Branch
    __tablename__ = 'apTakesPlace'
    __idField__ = 'idAp, idBranch'
    __compoundIdField__ = True

    idAp: int
    idBranch: int
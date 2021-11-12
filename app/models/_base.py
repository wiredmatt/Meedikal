from dataclasses import asdict, dataclass
import typing

from util.db import getDb

db = getDb()
cursor = db.cursor()

def getTotal(tablename:str, operator:str='AND', data:dict={}) -> int:
    _module = __import__('models')
    _class:'BaseModel' = getattr(_module, tablename[:1].upper() + tablename[1:])
    return _class.count(data or {}, operator)

@dataclass
class BaseModel:
    __tablename__ = 'baseModel'
    __idField__ = 'id'
    __compoundIdField__ = False

    def _dict(self) -> dict:
        return asdict(self)

    def _keys(self) -> list[str]:
        return [k for k in self._dict().keys()]

    def _values(self) -> list:
        return [v for v in self._dict().values()]

    def __init_subclass__(cls, *args, **kwargs): # make fields that were not provided None, sqlite will throw an error anyways.
        for field, value in cls.__annotations__.items():
            cls.__annotations__[field] = typing.Union[value, None]
            if not hasattr(cls, field):
                setattr(cls, field, None)
            if type(getattr(cls, field)) == type(str):
                if getattr(cls, field).strip() == '':
                    setattr(cls, field, None)

        super().__init_subclass__(*args, **kwargs)

    @classmethod
    def selectAll(cls) -> list['BaseModel']:
        statment = f"""SELECT * FROM {cls.__tablename__}"""
        result = db.execute(statment).fetchall()
        return [cls(*r) for r in result]

    @classmethod
    def buildQueryComponents(cls, items:dict={}) -> tuple:
        tables = [cls.__tablename__]
        conditions = []
        values = []

        for k, v in items.items():
            joins = False
            value = v
            _operator = '='
            k = str(k)

            if '.' in k:
                table = k.split(".")[0] #table.attribute
                
                if table not in tables:
                    tables.append(table)
            else:
                k = f'{cls.__tablename__}.{k}'
                
            if isinstance(v, dict):
                _operator = v.get('operator', '=' if v.get('value', None) is not None else 'IS')                  
                value = v.get('value', None)
                joins = v.get('joins', False)
            
            if joins:
                table = str(value).split(".")[0]
                if table not in tables:
                    tables.append(table)
                conditions.append(f"{k} {_operator} {value}")
            else:
                conditions.append(f"{k} {_operator} ?")
                values.append(value)
        
        print(conditions, values)

        return conditions, values, tables

    @classmethod
    def select(cls, items:dict={}, operator:str='AND', offset:int=None, limit:int=None, shape:str='list') -> typing.Union['BaseModel', list['BaseModel']]:
                    
        conditions, values, tables = cls.buildQueryComponents(items)

        statement = f"""
                    SELECT {cls.__tablename__}.* FROM {", ".join(tables)} 
                    {'WHERE ' + f" {operator} ".join(conditions) if len(conditions) > 0 else ''}
                    {f"LIMIT {limit} OFFSET {offset}" if limit is not None and offset is not None else ''}
                    """
                    
        result = db.execute(statement, values)
        if shape == 'list':
            return [cls(*r) for r in result.fetchall()]
        else:
            result = result.fetchone()
        
            if result:
                return cls(*result)
            else:
                return None

    @classmethod
    def selectOne(cls, items:dict, operator='AND') -> 'BaseModel':
        return cls.select(items=items, operator=operator, shape='one')

    @classmethod
    def selectMany(cls, items:dict, operator='AND', offset:int=None, limit:int=None) -> list['BaseModel']:
        return cls.select(items=items, operator=operator, offset=offset, limit=limit, shape='list')

    @classmethod
    def count(cls, items:dict, operator='AND') -> int:
        conditions, values, tables = cls.buildQueryComponents(items)

        statement = f"""
                    SELECT COUNT(*) FROM {", ".join(tables)} 
                    {'WHERE ' + f" {operator} ".join(conditions) if len(conditions) > 0 else ''}
                    """
                    
        result = db.execute(statement, values)

        return result.fetchone()[0]

    def insert(self, commit=True) -> 'BaseModel':
        statement = f"""
                    INSERT INTO {self.__tablename__}
                    ({",".join(self._keys())})
                    VALUES ({",".join("?"*len(self._values()))})
                    """

        cursor.execute(statement, self._values())
        
        if commit:
            db.commit()

            lastrowid = cursor.lastrowid # tables that automatically generate id
            
            if getattr(self, self.__idField__, None) is None:
                if ',' not in self.__idField__:
                    setattr(self, self.__idField__, lastrowid)
        
        return self
    
    def update(self, items:dict, commit=True) -> 'BaseModel':
        sets = ", ".join(f'{k} = ?' for k in items.keys())

        filters = " AND ".join([f"{k} = ?" if v is not None else f"{k} IS ?" for k,v in self._dict().items()])
        oldValues = [v for v in self._values()]
        
        newValues = [v for v in items.values()]

        statement = f"""
                    UPDATE {self.__tablename__}
                    SET {sets}
                    WHERE {filters}
                    """

        values = newValues + oldValues
        # print(statement,values)
        cursor.execute(statement, values) # updates the row in the db
        
        for k, v in items.items():
            setattr(self, k, v) # updates the attributes of this object

        if commit:
            db.commit()
        
        return self

    def delete(self, commit:bool=True) -> bool:

        filters = " AND ".join([f"{k} = ?" if v is not None else f"{k} IS ?" for k,v in self._dict().items()])
        values = [v for v in self._values()]

        statement = f"""DELETE FROM {self.__tablename__}
                        WHERE {filters}
                    """

        cursor.execute(statement, values)

        if commit:
            db.commit()

        return True if cursor.rowcount > 0 else False

    def insertOrSelect(self, idField=None, commit=True) -> 'BaseModel':
        try:
            return self.insert(commit)
        except: # record already exists
            if idField is not None:
                return self.selectOne({idField : getattr(self, idField)})
            else:
                if not self.__compoundIdField__:
                    return self.selectOne({self.__idField__ : getattr(self, self.__idField__)})
                else:
                    idfields = self.__idField__.split(",")
                    conditions = {}
                    for idF in idfields:
                        conditions[idF] = getattr(self, idF)
                    return self.selectOne(conditions)
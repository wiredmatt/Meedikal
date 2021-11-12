from models._base import BaseModel
from util.errors import ResourceNotFound, ExtensionNotAllowedError
from util.returnMessages import genericErrorReturn
from flask import request
from functools import wraps
from models import getTotal

def passJsonData(f):
    @wraps(f)
    def decorator(*args,**kwargs):
        data = request.get_json() or {}
        return f(*args, **kwargs, data=data)
    
    return decorator

def passFile(allowedExtensions:list[str]):
    def decorator(f):
        @wraps(f)
        def wrapper(*args,**kwargs):
            file = request.files.get('file', None)
            if file is None:
                return genericErrorReturn('missing file in formData')
            
            extension = file.filename.rsplit('.')[1].lower()
            if extension not in allowedExtensions:
                raise ExtensionNotAllowedError(allowedExtensions, extension)
            else:
                return f(*args, **kwargs, file=file)
        
        return wrapper
    return decorator

def paginated(offset:int=0, limit:int=10, max:int=10, tablename:str=None):
    def decorator(f):
        @passJsonData
        @wraps(f)
        def wrapper(data:dict={}, *args, **kwargs):
            total = max

            if tablename is not None:
                total = getTotal(tablename, data=data)

            _offset = offset
            _limit = limit

            _data = request.args

            if 'offset' in _data:
                _offset = int(_data['offset'])

            if 'limit' in _data:
                _limit = int(_data['limit'])

            if _offset < 0:
                _offset = 0

            if _limit > total:
                _limit = total
                _offset = _limit - 1

            return f(*args, **kwargs, offset=_offset, limit=_limit, total=total, data=data)
        
        return wrapper
    return decorator

def resourceExists(Model:BaseModel, idFields:list[str], idArgs:list[str], abort=True):
    def decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            conditions = {}

            for arg, idF in zip(idArgs, idFields):
                conditions[idF] = request.view_args.get(arg)

            obj = Model.selectOne(conditions)

            if obj is None and abort:
                raise ResourceNotFound

            return f(obj=obj, *args, **kwargs)
        
        return wrapper
    return decorator

def validDataValues(Model:BaseModel, idFields:list[str], dataKeys:list[str], abort=True):
    def decorator(f):
            @wraps(f)
            @passJsonData
            def wrapper(data:dict={},*args, **kwargs):
                conditions = {}

                for key, idF in zip(dataKeys, idFields):
                    conditions[idF] = data.get(key)

                obj = Model.selectOne(conditions)

                if obj is None and abort:
                    raise ResourceNotFound

                return f(*args, **kwargs)
            
            return wrapper
    return decorator
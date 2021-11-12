from models.User import *
from flask import Request

def parseRole(request:Request) -> str:
    try:
        return request.get_json()['extraFilters']['role']
    except:
        return None
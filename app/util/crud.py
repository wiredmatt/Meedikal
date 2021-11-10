from dataclasses import asdict
from models._base import BaseModel
from flask import jsonify

def crudReturn(result=None, paginationData=None):
    code = 200
    if isinstance(result, BaseModel):
        result = asdict(result)

    elif isinstance(result,list):
        for i in range(len(result)):
            if isinstance(result[i], BaseModel):
                result[i] = asdict(result[i]) # make it json serializable
        # if len(result) < 1:
        #     code = 404

    # elif result is None or result is False:
    #     code = 404

    data:dict = {"result": result}

    if paginationData:
        data['paginationData'] = paginationData

    return jsonify(data), code
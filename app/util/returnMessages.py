def genericErrorReturn(errMessage=None, extraMessage=None, code=400):
    return {"error": errMessage, "extraMessage": extraMessage}, code

def zeroRowReturn():
    return genericErrorReturn("zero rows matched the specified conditions", code=404)

def recordDoesntExist(tablename:str="record"):
    return genericErrorReturn(f"{tablename} doesn't exist")

def recordAlreadyExists(tablename:str="record", extraMessage=None):
    return genericErrorReturn(f"{tablename} already exists", extraMessage)

def provideData(extraMessage:str=None):
    return genericErrorReturn("no data was provided or it was invalid", extraMessage, 412)
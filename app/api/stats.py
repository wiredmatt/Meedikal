from flask import Blueprint
from util.crud import crudReturn
from middleware.authGuard import requiresRole
from middleware.data import passJsonData
from models._base import db
router = Blueprint('stats', __name__, url_prefix='/stats')

@router.get('/appointmentsMade')
@router.post('/appointmentsMade')
@requiresRole(['administrative'])
@passJsonData
def appointmentsMade(data:dict={}, **kwargs):
    _from = data.get('timeInterval', {}).get('from', None)
    _to = data.get('timeInterval', {}).get('to', None)
    _id = data.get('id', None)
    _appointmentName = data.get('appointmentName', None)
    
    tables = ['appointment']
    conditions = []
    values = []

    if _from and _to:
        conditions.append('appointment.date >= ? and appointment.date <= ?') # ?1: _from, ?2: _to
        values.append(_from)
        values.append(_to)
    elif _from:
        conditions.append('appointment.date >= ?') # ?1: _from
        values.append(_from)
    elif _to:
        conditions.append('appointment.date <= ?') # ?1: _to
        values.append(_to)

    if _appointmentName:
        conditions.append("appointment.name LIKE ?")
        values.append(_appointmentName)

    if _id:
        conditions.append('assignedTo.idDoc = ?')
        conditions.append('assignedTo.idAp = appointment.id')
        tables.append('assignedTo')
        values.append(_id)

    statementCount = f"""SELECT COUNT(appointment.id) FROM {', '.join(tables)}
                    {' WHERE ' + ' AND '.join(conditions) if len(conditions) > 0 else ''}"""

    result = db.execute(statementCount, values).fetchone()[0]

    return crudReturn(result)

@router.get('/diagnosedDiseases')
@requiresRole(['administrative'])
def diagnosedDiseases(**kwargs):
    statement = f"""SELECT disease.id, disease.name, COUNT(disease.id) count
                    FROM diagnoses, disease
                    WHERE diagnoses.idDis = disease.id
                    GROUP BY diagnoses.idDis
                    ORDER BY COUNT DESC"""

    result = db.execute(statement).fetchall()

    data = []

    for r in result:
        data.append({'id': r[0], 'name': r[1], 'count': r[2]})

    return crudReturn(data)

@router.get('/registeredSymptoms')
@requiresRole(['administrative'])
def registeredSymptoms(**kwargs):
    statement = f"""SELECT symptom.id, symptom.name, COUNT(symptom.id) count
                    FROM registersSy, symptom
                    WHERE registersSy.idSy = symptom.id
                    GROUP BY registersSy.idSy
                    ORDER BY COUNT DESC"""

    result = db.execute(statement).fetchall()

    data = []

    for r in result:
        data.append({'id': r[0], 'name': r[1], 'count': r[2]})

    return crudReturn(data)
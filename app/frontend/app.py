from dataclasses import asdict
from flask import Blueprint, render_template, request, redirect
from config import Config
from models.User import User, Doctor
from models.Branch import *
from models.Appointment import *
from models.Disease import *
from models.Symptom import *
from models.ClinicalSign import *
from middleware.authGuard import getCurrentRole, requiresRole, requiresAuth
from api.users import userToReturn
from datetime import date

appRouter = Blueprint('app', __name__, url_prefix='app') # handles /app

baseDir = 'pages'
baseDirApp = f'{baseDir}/app'

@appRouter.get('')
@appRouter.get('/')
@requiresAuth
def home(**any):
    return render_template(f'{baseDirApp}/home.html')

@appRouter.get('/profile')
@getCurrentRole
def profile(id:int, currentRole:str):
    user = userToReturn(User.select({'id': id}), id, currentRole, currentRole)
    return render_template(f'{baseDirApp}/profile.html', user=user, readOnly=False)

@appRouter.get('/profile/<int:idUser>')
@appRouter.get('/profile/<int:idUser>/<string:asRole>')
@requiresAuth
def profileById(idUser:int, asRole:str=None, *args, **kwargs):
    user = userToReturn(User.select({'id': id})(idUser), **kwargs, role=asRole)
    return render_template(f'{baseDirApp}/view-profile.html', user=user, asRole=asRole, readOnly=True)

@appRouter.get('/appointments')
@requiresAuth
def appointments(**any):
    return render_template(f'{baseDirApp}/appointments.html', idUser=False, timeFilter=False, readOnly=False)

@appRouter.get('/appointments/<int:id>') # show all the patients attending to this appointment
@requiresRole(['doctor', 'administrative'])
@getCurrentRole
def scheduledAppointments(id:int, **kwargs):
    appointment = asdict(Appointment.getById(id))
    assignedDoctor = userToReturn(Doctor.getDocOfAp(id), **kwargs)
    branch = Branch.getBranchOfAp(id)

    if branch:
        branch = asdict(branch)

    attendingPatients = AttendsTo.select(id) or []
    if len(attendingPatients) > 0:
        attendingPatients = [asdict(atp) for atp in attendingPatients]
        for atp in attendingPatients:
            atp['patient'] = userToReturn(User.select({'id': id})(atp['idPa']), **kwargs)

    return render_template(f'{baseDirApp}/scheduled-patients.html', appointment=appointment, branch=branch, assignedDoctor=assignedDoctor, attendingPatients=attendingPatients)

@appRouter.get('/appointments/patient/<int:idUser>') # show all scheduled appointments for this patient
@requiresAuth
def patientScheduledAppointments(idUser:int, **kw):
    return render_template(f'{baseDirApp}/appointments.html', idUser=idUser, timeFilter='all', readOnly=True)

@appRouter.get('/appointments/doctor/<int:idUser>') # show all scheduled appointments for this doctor
@requiresAuth
def doctorScheduledAppointments(idUser:int, **kw):
    return render_template(f'{baseDirApp}/appointments.html', idUser=idUser, timeFilter='all', readOnly=True)

@appRouter.get('/appointment/<int:id>/<int:idUser>') # view details of an specific appoitment of a patient
@getCurrentRole
def appointmentById(id:int, idUser:int, **kwargs):
    ap = asdict(Appointment.getById(id))
    attendsTo = AttendsTo.select({'idAp': id, 'idPa': idUser}, returns='one')
    doctor = userToReturn(Doctor.getDocOfAp(id), **kwargs, role='doctor') or {}
    branch = Branch.getBranchOfAp(id)
    patient = userToReturn(User.select({'id': id})(idUser), **kwargs)

    if isinstance(branch, Branch):
        branch = asdict(branch)

    if isinstance(attendsTo, AttendsTo):
        attendsTo = asdict(attendsTo)

    diagnosedDiseases = Diagnoses.select({'idPa': idUser, 'idAp': id}) or []
    if len(diagnosedDiseases) > 0:
        diagnosedDiseases = [asdict(d) for d in diagnosedDiseases]

        for diagnosed in diagnosedDiseases:
            diagnosed['name'] = Disease.getById(diagnosed['idDis']).name
    
    registeredSymptoms = RegistersSy.select({'idPa': idUser, 'idAp': id}) or []
    if len(registeredSymptoms) > 0:
        registeredSymptoms = [asdict(s) for s in registeredSymptoms]

        for registered in registeredSymptoms:
            registered['name'] = Symptom.getById(registered['idSy']).name
    
    registeredCs = RegistersCs.select({'idPa': idUser, 'idAp': id}) or []
    if len(registeredCs) > 0:
        registeredCs = [asdict(cs) for cs in registeredCs]

        for registered in registeredCs:
            registered['name'] = ClinicalSign.getById(registered['idCs']).name

    return render_template(f'{baseDirApp}/appointment-details.html', attendsTo=attendsTo,
                            appointment=ap, branch=branch, doctor=doctor, patient=patient,
                            diagnosedDiseases=diagnosedDiseases, 
                            registeredSymptoms=registeredSymptoms,
                            registeredCs=registeredCs)

@appRouter.get('/symptoms')
@appRouter.get('/clinical-signs')
@appRouter.get('/diseases')
@requiresAuth
def symptoms(**any):
    return render_template(f'{baseDirApp}/sufferings.html')

@appRouter.get('/create-symptom')
@requiresRole(['doctor', 'administrative'])
def createSymptom(**any):
    return render_template(f'{baseDirApp}/suffering.html', sufferingType='symptom', suffering={})

@appRouter.get('/create-clinical-sign')
@requiresRole(['doctor', 'administrative'])
def createClinicalSign(**any):
    return render_template(f'{baseDirApp}/suffering.html', sufferingType='clinicalSign', suffering={})

@appRouter.get('/create-disease')
@requiresRole(['doctor', 'administrative'])
def createDisease(**any):
    return render_template(f'{baseDirApp}/suffering.html', sufferingType='disease', suffering={})

@appRouter.get('/update-symptom/<int:id>')
@requiresRole(['doctor', 'administrative'])
def updateSymptom(id:int, **any):
    symptom = Symptom.getById(id)
    if symptom is None:
        return redirect('/app/symptoms')
    
    symptom = asdict(symptom)
    return render_template(f'{baseDirApp}/suffering.html', sufferingType='symptom', suffering=symptom)

@appRouter.get('/update-clinical-sign/<int:id>')
@requiresRole(['doctor', 'administrative'])
def updateClinicalSign(id:int, **any):
    clinicalSign = ClinicalSign.getById(id)
    if clinicalSign is None:
        return redirect('/app/clinical-signs')
    
    clinicalSign = asdict(clinicalSign)
    return render_template(f'{baseDirApp}/suffering.html', sufferingType='clinicalSign', suffering=clinicalSign)

@appRouter.get('/update-disease/<int:id>')
@requiresRole(['doctor', 'administrative'])
def updateDisease(id:int, **any):
    disease = Disease.getById(id)
    if disease is None:
        return redirect('/app/diseases')
    
    disease = asdict(disease)

    return render_template(f'{baseDirApp}/suffering.html', sufferingType='disease', suffering=disease)

@appRouter.get('/symptom/<int:id>')
@requiresAuth
def readSymptom(id:int, **any):
    symptom = Symptom.getById(id)
    if symptom is None:
        return redirect('/app/symptoms')
    
    symptom = asdict(symptom)

    return render_template(f'{baseDirApp}/read-suffering.html', sufferingType='symptom', suffering=symptom)

@appRouter.get('/clinical-sign/<int:id>')
@requiresAuth
def readCs(id:int, **any):
    cs = ClinicalSign.getById(id)
    if cs is None:
        return redirect('/app/clinical-signs')
    
    cs = asdict(cs)

    return render_template(f'{baseDirApp}/read-suffering.html', sufferingType='clinicalSign', suffering=cs)
    
@appRouter.get('/disease/<int:id>')
@requiresAuth
def readDisease(id:int, **any):
    disease = Disease.getById(id)
    if disease is None:
        return redirect('/app/diseases')
    
    disease = asdict(disease)

    return render_template(f'{baseDirApp}/read-suffering.html', sufferingType='disease', suffering=disease)
    
@appRouter.get('/branches')
def branches():
    return render_template(f'{baseDirApp}/branches.html', branches=Branch.query(), selectedBranch=None, assignMode=False)

@appRouter.get('/settings')
@requiresAuth
def settings(id:int, **any):
    myRoles = User.getRoles(id)
    return render_template(f'{baseDirApp}/settings.html', myRoles=myRoles)

# mp specifics
@appRouter.get('/patients')
@requiresRole(['doctor'])
def patients():
    return render_template(f'{baseDirApp}/patients.html')

# administrative specifics

@appRouter.get('/users')
@requiresRole(['administrative'])
def users():
    return render_template(f'{baseDirApp}/administrative/users.html')

@appRouter.get('/create-user')
@requiresRole(['administrative'])
def createUser():
    return render_template(f'{baseDirApp}/administrative/create-user.html')

@appRouter.get('/update-user/<int:idUser>')
@getCurrentRole
@requiresRole(['administrative'])
def updateUser(idUser:int, **kwargs):
    user = userToReturn(User.select({'id': id})(idUser), **kwargs)
    return render_template(f'{baseDirApp}/administrative/update-user.html', user=user)

@appRouter.get('/create-branch')
@requiresRole(['administrative'])
def createBranch():
    return render_template(f'{baseDirApp}/administrative/branch.html', branch={})

@appRouter.get('/update-branch/<int:id>')
@requiresRole(['administrative'])
def updateBranch(id:int):
    branch = asdict(Branch.getById(id))
    return render_template(f'{baseDirApp}/administrative/branch.html', branch=branch)

@appRouter.get('/create-appointment')
@requiresRole(['administrative'])
def createAppointment():
    branches = Branch.query()
    selectedBranch = {}
    
    if len(branches) > 0:
        branches = [asdict(b) for b in branches]
        selectedBranch = branches[0]

    return render_template(f'{baseDirApp}/administrative/appointment.html', appointment={},
                           selectedBranch=selectedBranch, branches=branches,
                           selectedDoctor={}, assignMode=True)

@appRouter.get('/update-appointment/<int:id>')
@getCurrentRole
@requiresRole(['administrative'])
def updateAppointment(id:int, **kwargs):
    appointment = asdict(Appointment.getById(id))
    branches = Branch.query()
    
    if len(branches) > 0:
        branches = [asdict(b) for b in branches]

    _selectedBranch = Branch.getBranchOfAp(id)
    if isinstance(_selectedBranch, Branch):
        selectedBranch = asdict(_selectedBranch)
    else:
        selectedBranch = {}

    _selectedDoctor = Doctor.getDocOfAp(id) 
    if isinstance(_selectedDoctor, User):
        selectedDoctor = userToReturn(_selectedDoctor, **kwargs, role='doctor')
    else:
        selectedDoctor = {}

    return render_template(f'{baseDirApp}/administrative/appointment.html', appointment=appointment, branches=branches, selectedBranch=selectedBranch, selectedDoctor=selectedDoctor, assignMode=True)

# @appRouter.get('/stats')
# @requiresRole(['administrative'])
# def stats():
#     return render_template(f'{baseDirApp}/administrative/stats.html')

@appRouter.context_processor
@getCurrentRole
def appVars(id:int, currentRole:str):
    url = request.url.split('/app', 1)[1]
    if url == '/':
        url = 'home'
    else:
        url = url.split('/')[1]
        url = url.replace('-', ' ')

    return dict(myRole=currentRole, me=userToReturn(User.select({'id': id}), id, currentRole, role=currentRole), 
    appPages=Config.app_pages, roleColors=Config.role_colors,
    currentPage=url.capitalize(), currentDate = date.today())
from dataclasses import asdict
from flask import Blueprint, render_template, request
from api.appointments import appointmentExists
from api.branches import branchExists
from api.sufferings import sufferingExists
from api.users import userExists
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
def home(**kwargs):
    return render_template(f'{baseDirApp}/home.jinja2')

@appRouter.get('/profile')
@getCurrentRole
def profile(id:int, currentRole:str, **kwargs):
    user = userToReturn(User.selectOne({'id': id}), id, currentRole, currentRole)
    return render_template(f'{baseDirApp}/profile.jinja2', user=user, readOnly=False)

@appRouter.get('/profile/<int:idUser>')
@appRouter.get('/profile/<int:idUser>/<string:asRole>')
@requiresAuth
@userExists()
def profileById(user:User, asRole:str=None, **kwargs):
    user = userToReturn(user, **kwargs, role=asRole)
    return render_template(f'{baseDirApp}/view-profile.jinja2', user=user, asRole=asRole, readOnly=True)

@appRouter.get('/appointments')
@requiresAuth
def appointments(**kwargs):
    return render_template(f'{baseDirApp}/appointments.jinja2', idUser=False, timeFilter=False, readOnly=False)

@appRouter.get('/appointments/<int:idAp>') # show all the patients attending to this appointment
@requiresRole(['doctor', 'administrative'])
@getCurrentRole
@appointmentExists()
def scheduledAppointments(appointment:Appointment, **kwargs):
    appointment = asdict(appointment)
    assignedDoctor = userToReturn(Doctor.getDocOfAp(appointment.id), **kwargs)
    branch = Branch.getBranchOfAp(appointment.id)

    if branch:
        branch = asdict(branch)

    attendingPatients = AttendsTo.selectMany({'idAp': appointment.id}) or []
    if len(attendingPatients) > 0:
        attendingPatients = [asdict(atp) for atp in attendingPatients]
        for atp in attendingPatients:
            atp['patient'] = userToReturn(User.select({'id': atp['idPa']}), **kwargs)

    return render_template(f'{baseDirApp}/scheduled-patients.jinja2', appointment=appointment, branch=branch, assignedDoctor=assignedDoctor, attendingPatients=attendingPatients)

@appRouter.get('/appointments/patient/<int:idUser>') # show all scheduled appointments for this patient
@requiresAuth
@userExists(Patient)
def patientScheduledAppointments(patient:Patient, **kwargs):
    return render_template(f'{baseDirApp}/appointments.jinja2', idUser=patient.id, timeFilter='all', readOnly=True)

@appRouter.get('/appointments/doctor/<int:idUser>') # show all scheduled appointments for this doctor
@requiresAuth
@userExists(Doctor)
def doctorScheduledAppointments(doctor:Doctor, **kwargs):
    return render_template(f'{baseDirApp}/appointments.jinja2', idUser=doctor.id, timeFilter='all', readOnly=True)

@appRouter.get('/appointment/<int:idAp>/<int:idUser>') # view details of an specific appoitment of a patient
@getCurrentRole
@userExists(User)
@appointmentExists(AttendsTo, ['idAp', 'idPa'], ['idAp', 'idUser'])
def appointmentDetails(appointment:AttendsTo, user:User, **kwargs):
    attendsTo = asdict(appointment)
    appointment = asdict(Appointment.selectOne({'id': attendsTo['idAp']}))
    doctor = userToReturn(Doctor.getDocOfAp(appointment['id']), **kwargs, role='doctor') or {}
    branch = Branch.getBranchOfAp(appointment['id'])
    patient = userToReturn(user, **kwargs)

    if isinstance(branch, Branch):
        branch = asdict(branch)

    diagnosedDiseases = Diagnoses.selectMany({'idPa': user.id, 'idAp': appointment['id']}) or []
    if len(diagnosedDiseases) > 0:
        diagnosedDiseases = [asdict(d) for d in diagnosedDiseases]

        for diagnosed in diagnosedDiseases:
            diagnosed['name'] = Disease.selectOne({'id': diagnosed['idDis']}).name
    
    registeredSymptoms = RegistersSy.selectMany({'idPa': user.id, 'idAp': appointment['id']}) or []
    if len(registeredSymptoms) > 0:
        registeredSymptoms = [asdict(s) for s in registeredSymptoms]

        for registered in registeredSymptoms:
            registered['name'] = Symptom.selectOne({'id': registered['idSy']}).name
    
    registeredCs = RegistersCs.selectMany({'idPa': user.id, 'idAp': appointment['id']}) or []
    if len(registeredCs) > 0:
        registeredCs = [asdict(cs) for cs in registeredCs]

        for registered in registeredCs:
            registered['name'] = ClinicalSign.selectOne({'id': registered['idCs']}).name

    return render_template(f'{baseDirApp}/appointment-details.jinja2', attendsTo=attendsTo,
                            appointment=appointment, branch=branch, doctor=doctor, patient=patient,
                            diagnosedDiseases=diagnosedDiseases, 
                            registeredSymptoms=registeredSymptoms,
                            registeredCs=registeredCs)

@appRouter.get('/symptoms')
@appRouter.get('/clinical-signs')
@appRouter.get('/diseases')
@requiresAuth
def symptoms(**kwargs):
    return render_template(f'{baseDirApp}/sufferings.jinja2')

@appRouter.get('/create-symptom')
@requiresRole(['doctor', 'administrative'])
def createSymptom(**kwargs):
    return render_template(f'{baseDirApp}/suffering.jinja2', sufferingType='symptom', suffering={})

@appRouter.get('/create-clinical-sign')
@requiresRole(['doctor', 'administrative'])
def createClinicalSign(**kwargs):
    return render_template(f'{baseDirApp}/suffering.jinja2', sufferingType='clinicalSign', suffering={})

@appRouter.get('/create-disease')
@requiresRole(['doctor', 'administrative'])
def createDisease(**kwargs):
    return render_template(f'{baseDirApp}/suffering.jinja2', sufferingType='disease', suffering={})

@appRouter.get('/update-symptom/<int:idS>')
@requiresRole(['doctor', 'administrative'])
@sufferingExists(Model=Symptom)
def updateSymptom(suffering:Symptom, **kwargs):
    symptom = asdict(suffering)
    return render_template(f'{baseDirApp}/suffering.jinja2', sufferingType='symptom', suffering=symptom)

@appRouter.get('/update-clinical-sign/<int:idS>')
@requiresRole(['doctor', 'administrative'])
@sufferingExists(Model=ClinicalSign)
def updateClinicalSign(suffering:ClinicalSign, **kwargs):
    clinicalSign = asdict(suffering)
    return render_template(f'{baseDirApp}/suffering.jinja2', sufferingType='clinicalSign', suffering=clinicalSign)

@appRouter.get('/update-disease/<int:idS>')
@requiresRole(['doctor', 'administrative'])
@sufferingExists(Model=Disease)
def updateDisease(suffering:Disease, **kwargs):
    disease = asdict(suffering)
    return render_template(f'{baseDirApp}/suffering.jinja2', sufferingType='disease', suffering=disease)

@appRouter.get('/symptom/<int:idS>')
@requiresAuth
@sufferingExists(Model=Symptom)
def readSymptom(suffering:Symptom, **kwargs):
    symptom = asdict(suffering)
    return render_template(f'{baseDirApp}/read-suffering.jinja2', sufferingType='symptom', suffering=symptom)

@appRouter.get('/clinical-sign/<int:idS>')
@requiresAuth
@sufferingExists(Model=ClinicalSign)
def readCs(suffering:ClinicalSign, **kwargs):
    cs = asdict(suffering)
    return render_template(f'{baseDirApp}/read-suffering.jinja2', sufferingType='clinicalSign', suffering=cs)
    
@appRouter.get('/disease/<int:idS>')
@requiresAuth
@sufferingExists(Model=Disease)
def readDisease(suffering:Disease, **kwargs):
    disease = asdict(suffering)
    return render_template(f'{baseDirApp}/read-suffering.jinja2', sufferingType='disease', suffering=disease)
    
@appRouter.get('/branches')
@requiresAuth
def branches(**kwargs):
    return render_template(f'{baseDirApp}/branches.jinja2', branches=Branch.selectAll(), selectedBranch=None, assignMode=False)

@appRouter.get('/settings')
@requiresAuth
def settings(id:int, **kwargs):
    myRoles = User.getRoles(id)
    return render_template(f'{baseDirApp}/settings.jinja2', myRoles=myRoles)

@appRouter.get('/patients')
@requiresRole(['doctor'])
def patients(**kwargs):
    return render_template(f'{baseDirApp}/patients.jinja2')

# administrative specifics

@appRouter.get('/users')
@requiresRole(['administrative'])
def users(**kwargs):
    return render_template(f'{baseDirApp}/administrative/users.jinja2')

@appRouter.get('/create-user')
@requiresRole(['administrative'])
def createUser(**kwargs):
    return render_template(f'{baseDirApp}/administrative/create-user.jinja2')

@appRouter.get('/update-user/<int:idUser>')
@requiresRole(['administrative'])
@getCurrentRole
@userExists()
def updateUser(user:User, **kwargs):
    user = userToReturn(user, **kwargs)
    return render_template(f'{baseDirApp}/administrative/update-user.jinja2', user=user)

@appRouter.get('/create-branch')
@requiresRole(['administrative'])
def createBranch(**kwargs):
    return render_template(f'{baseDirApp}/administrative/branch.jinja2', branch={})

@appRouter.get('/update-branch/<int:idB>')
@requiresRole(['administrative'])
@branchExists()
def updateBranch(branch, **kwargs):
    branch = asdict(branch)
    return render_template(f'{baseDirApp}/administrative/branch.jinja2', branch=branch)

@appRouter.get('/create-appointment')
@requiresRole(['administrative'])
def createAppointment(**kwargs):
    branches = Branch.selectAll()
    selectedBranch = {}
    
    if len(branches) > 0:
        branches = [asdict(b) for b in branches]
        selectedBranch = branches[0]

    return render_template(f'{baseDirApp}/administrative/appointment.jinja2', appointment={},
                           selectedBranch=selectedBranch, branches=branches,
                           selectedDoctor={}, assignMode=True)

@appRouter.get('/update-appointment/<int:idAp>')
@requiresRole(['administrative'])
@getCurrentRole
@appointmentExists()
def updateAppointment(appointment:Appointment, **kwargs):
    appointment = asdict(appointment)
    branches = Branch.selectAll()
    
    if len(branches) > 0:
        branches = [asdict(b) for b in branches]

    selectedBranch = Branch.getBranchOfAp(appointment.id) or {}
    if isinstance(selectedBranch, Branch):
        selectedBranch = asdict(selectedBranch)

    selectedDoctor = Doctor.getDocOfAp(appointment.id) or {} 
    if isinstance(selectedDoctor, User):
        selectedDoctor = userToReturn(selectedDoctor, **kwargs, role='doctor')

    return render_template(f'{baseDirApp}/administrative/appointment.jinja2', appointment=appointment, branches=branches, selectedBranch=selectedBranch, selectedDoctor=selectedDoctor, assignMode=True)

# @appRouter.get('/stats')
# @requiresRole(['administrative'])
# def stats():
#     return render_template(f'{baseDirApp}/administrative/stats.jinja2')

@appRouter.context_processor
@getCurrentRole
def appVars(id:int, currentRole:str):
    url = request.url.split('/app', 1)[1]
    if url == '/':
        url = 'home'
    else:
        url = url.split('/')[1]
        url = url.replace('-', ' ')

    return dict(myRole=currentRole, me=userToReturn(User.selectOne({'id': id}), id, currentRole, role=currentRole), 
    appPages=Config.app_pages, roleColors=Config.role_colors,
    currentPage=url.capitalize(), currentDate=date.today())
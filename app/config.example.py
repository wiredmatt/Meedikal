# rename to config.py
from dataclasses import dataclass

@dataclass
class Plan:
    name: str
    price: float
    popular: bool
    features: list[str]
    legendText: str

@dataclass
class Page:
    route: str
    name: str

class AppPage(Page):
    accessibleBy: list[str]
    icon: str

    def __init__(self, route:str, name:str, accessibleBy:list[str]=['user', 'patient', 'medicalPersonnel', 'doctor', 'administrative'], icon:str=None):
        super().__init__(route, name)
        self.accessibleBy = accessibleBy
        if icon is not None:
            self.icon = icon
        else:
            self.icon = 'icons/home.svg'

class Config(object):
    DEBUG = False
    TESTING = False
    SESSION_COOKIE_SAMESITE = 'Strict'
    JSON_SORT_KEYS = False
    SECRET_KEY = 'secretkey' # used to sign and verify jwt tokens
    DATABASE = 'meedikal.db'
    UPLOAD_FOLDER = 'images/'
    Admin = {
        'id': 12345678,
        'name1': 'Juan',
        'surname1': 'Perez',
        'sex': 'M',
        'birthdate': '1992-08-08',
        'location': 'Street 123',
        'email': 'juanperez@gmail.com',
        'password': '1234',
        'name2': 'Marcos',
        'surname2': 'Gonzalez',
        'genre': 'Male',
        'active': 1,
    }
    
    company_name = 'Healthcare Company'
    
    central_data = {
        'address': 'Jorge Canning 2363, Montevideo',
        'email': 'support@hccompay.com',
        'phone': '123-456-7890',
        'google_maps_link': 'https://www.google.com/maps/embed?pb=!1m14!1m8!1m3!1d13095.168728844454!2d-56.1938193!3d-34.8614488!3m2!1i1024!2i768!4f13.1!3m3!1m2!1s0x0%3A0xa3c298c9fd703d35!2sSociedad%20M%C3%A9dica%20Universal!5e0!3m2!1sen!2suy!4v1633202238613!5m2!1sen!2suy'
        }

    role_colors = {
        'user': 'bg-gray-300',
        'administrative': 'bg-red-500',
        'patient': 'bg-turqoise',
        'medicalPersonnel': 'bg-skyblue',
        'doctor': 'bg-darker-skyblue',
    }

    plans = [
        Plan(name='Plan 1',
            price=100,
            popular=False, 
            features=['feature 1',
                      'feature 2',
                      'feature 3'],
            legendText='Initial Plan.'),
        
        Plan(name='Plan 2',
            price=190, 
            popular=True,
            features=['feature 1',
                      'feature 2',
                      'feature 3',
                      'feature 4',
                      'feature 5'],
            legendText='Pro Plan.'),
        
        Plan(name='Plan 3', 
            price=400, 
            popular=False,
            features=['feature 1',
                      'feature 2',
                      'feature 3',
                      'feature 4',
                      'feature 5',
                      'feature 6'],
            legendText='Family Plan.'),
        
        Plan(name='Plan 4', 
            price=750, 
            popular=False, 
            features=['feature 1',
                      'feature 2',
                      'feature 3',
                      'feature 4',
                      'feature 5',
                      'feature 6',
                      'feature 7'],
            legendText='Golden Plan.'),
    ]

    landing_pages = [
        Page(route='/', name='Home'), 
        Page(route='/contact', name='Contact'), 
        Page(route='/plans', name='Plans')
        ]

    app_pages = [
        AppPage('/app', 'Home', icon='icons/home.svg'),
        AppPage('/app/users', 'Users', ['administrative'], icon='icons/users.svg'),
        AppPage('/app/appointments', 'Appointments', icon='icons/appointments.svg'),
        AppPage('/app/patients', 'Patients', ['doctor'], icon='icons/users.svg'),
        AppPage('/app/symptoms', 'Symptoms',  icon='icons/symptoms.svg'),
        AppPage('/app/diseases', 'Diseases', icon='icons/diseases.svg'),
        AppPage('/app/clinical-signs', 'Clinical Signs', icon='icons/clinical_signs.svg'),
        AppPage('/app/branches', 'Branches', icon='icons/branches.svg'),
        AppPage('/app/profile', 'Profile'),
    ]

class ProductionConfig(Config):
    DEBUG = False

class StagingConfig(Config):
    DEBUG = True

class DevelopmentConfig(Config):
    DEBUG = True
    ENV= "development"
class TestingConfig(Config):
    TESTING = True
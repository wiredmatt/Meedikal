import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(__file__)))
p = os.path.join(os.path.dirname(__file__))
from models.User import User

data = {
        'id': 1,
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

if __name__ == '__main__':
    for id in range(0,25):
        User(**data).insert()
        data['id'] = data['id'] + 1
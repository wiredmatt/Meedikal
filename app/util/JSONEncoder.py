import json
from datetime import date
from datetime import time
from datetime import datetime

class JsonExtendEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, datetime):
            return o.isoformat()
        elif isinstance(o, date):
            return o.isoformat()
        elif isinstance(o, time):
            return o.isoformat()
        else:
            return json.JSONEncoder.default(self, o)
import datetime
import json
import ast
import collections
import drchrono.endpoints as endpoints

class Appointment:

    def __init__(self, data):
        self.id = data['id']
        self.doctor =  data['doctor']
        self.office = data['office']
        self.patient = data['patient']
        self._exam_room = data['exam_room']
        self.duration = data['duration']
        self.scheduled_start_datetime = datetime.datetime.strptime(data['scheduled_time'], '%Y-%m-%dT%H:%M:%S')
        self.reason = data['reason']
        self.status = data['status']
        self.is_walk_in = data['is_walk_in']

    @classmethod
    def get(cls, id, token, shallow=True, data={}):
        api = endpoints.AppointmentEndpoint(token)
        data = collections.defaultdict(str, data)
        if not data:
            data = collections.defaultdict(str, api.fetch(id))
        if shallow:
            data['doctor'] = None
            data['office'] = None
            data['patient'] = None
        else:
            data['doctor'] = Doctor.get(data['doctor'], token)
            data['office'] = Office.get(data['office'], token)
            data['patient'] = Patient.get(data['patient'], token, shallow=True)

        return Appointment(data)

    @property
    def scheduled_end_datetime(self):
        if self.scheduled_start_datetime and self.duration:
            return self.scheduled_start_datetime + datetime.timedelta(minutes=float(self.duration))
        return None

    @property
    def scheduled_start_time(self):
        if self.scheduled_start_datetime:
            try:
                return self.scheduled_start_datetime.time().strftime('%I:%M %p')
            except:
                pass
        return None

    @property
    def scheduled_end_time(self):
        if self.scheduled_end_datetime:
            return self.scheduled_end_datetime.time().strftime('%I:%M %p')
        return None

    @property
    def exam_room(self):
        if self.office:
            try:
                return self.office.exam_rooms[self._exam_room - 1]
            except:
                pass
        
        return None

    def __str__(self):
        return str(self.__dict__)

class Doctor:

    def __init__(self, data):
        self.id = data['id']
        self.first_name = data['first_name']
        self.last_name = data['last_name']

    @classmethod
    def get(cls, id, token, shallow=True, data={}):
        api = endpoints.DoctorEndpoint(token)
        data = collections.defaultdict(str, data)
        if not data:
            data = collections.defaultdict(str, api.fetch(id))

        return Doctor(data)

    def __str__(self):
        return str(self.__dict__)

class Office:

    def __init__(self, data):

        self.id = data['id']
        self.name = data['name']
        self.exam_rooms = data['exam_rooms'] 

    @classmethod
    def get(cls, id, token, data={}):
        api = endpoints.OfficeEndpoint(token)
        data = collections.defaultdict(str, data)
        if not data:
            data = collections.defaultdict(str, api.fetch(id))

        return Office(data)
    
    def __str__(self):
        return str(self.__dict__)

class Patient:
    
    def __init__(self, data):
        self.id = data['id']
        self.doctor = data['doctor']
        self.first_name = data['first_name']
        self.last_name = data['last_name']
        self.gender = data['gender']
        self.city = data['city']
        self.ethnicity = data['ethnicity']
        self.race = data['race']

    @classmethod
    def get(cls, id, token, shallow=True, data={}):
        api = endpoints.PatientEndpoint(token)
        data = collections.defaultdict(str, data)
        if not data:
            data = collections.defaultdict(str, api.fetch(id))
        
        if shallow:
            data['doctor'] = None
        else:
            data['doctor'] = Doctor.get(data['doctor'], token)

        return Patient(data)

    def __str__(self):
        return str(self.__dict__)
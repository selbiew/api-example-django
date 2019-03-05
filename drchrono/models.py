import datetime
import json
import ast
import collections
import drchrono.endpoints
from django.db import models
from django.utils.timezone import make_aware

class Appointment():
    STATUS_CHOICES = (
        ('UNK', ''),
        ('ARR', 'Arrived'),
        ('CHK', 'Checked In'),
        ('CNC', 'Canceled'),
        ('CMP', 'Complete'),
        ('CNF', 'Confirmed'),
        ('INS', 'In Session'),
        ('NSH', 'No Show'),
        ('NCF', 'Not Confirmed'),
        ('RSC', 'Rescheduled'),
    )
    
    def __init__(self, id):
        self.id = data['id']
        # self.doctor =  get_doctor()
        # self.office = get_office()
        # self.patient = get_patient()
        # self.exam_room = get_exam_room()
        self.duration = data['duration']
        self.scheduled_start_datetime = data['scheduled_time']
        self.status = data['status']
        self.is_walk_in = data['is_walk_in']

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
    def wait_time(self):
        wait_time = 0
        if self.start_datetime and self.checkin_datetime:
            wait_time = self.start_datetime - self.checkin_datetime
        elif self.status == 'Checked In' and self.checkin_datetime:
            wait_time = datetime.datetime.now() - self.checkin_datetime
        
        return wait_time

    @property
    def exam_room(self):
        return self.office.exam_rooms[self._exam_room - 1]

    @classmethod
    def retrieve(cls, data):
        appointment, _ = cls.objects.update_or_create(id=data['id'], doctor_id=data['doctor'],
            duration=data['duration'], patient_id=data['patient'], reason=data['reason'],
            scheduled_start_datetime=data['scheduled_time'], status=data['status'],
            _exam_room=data['exam_room'],office_id=data['office'], is_walk_in=data['is_walk_in'],
        )

        return appointment  

class AppointmentProfile(models.Model):
    id = models.IntegerField(primary_key=True)
    doctor = models.ForeignKey('Doctor')
    duration = models.IntegerField()
    name = models.CharField(max_length=64, null=True)
    reason = models.CharField(max_length=1024, null=True)


    @classmethod
    def retrieve(cls, data):
        appointment_profile, _ = cls.objects.update_or_create(id=data['id'], doctor_id=data['doctor'],
        duration=data['duration'], name=data['name'], reason=data['reason'])

        return appointment_profile 

class Doctor(models.Model):
    id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64, null=True)

    @classmethod
    def retrieve(cls, data):
        doctor, _ = cls.objects.update_or_create(id=data['id'], first_name=data['first_name'],
            last_name=data['last_name'])
        
        return doctor  

class Office(models.Model):
    doctor = models.ForeignKey('Doctor')
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=64)
    _exam_rooms = models.CharField(max_length=2048)

    @property
    def exam_rooms(self):
        if self._exam_rooms:
            return json.loads(self._exam_rooms)
        return []

    @classmethod
    def retrieve(cls, data):
        office, _ = cls.objects.update_or_create(id=data['id'], name=data['name'],
            doctor_id=data['doctor'],
            _exam_rooms=json.dumps([exam_room['name'] for exam_room in data['exam_rooms']]),
        )
        
        return office  

class Patient(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    id = models.IntegerField(primary_key=True)
    # date_of_birth = models.DateField(null=True)
    doctor = models.ForeignKey('Doctor')
    gender = models.CharField(choices=GENDER_CHOICES, max_length=6, null=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64, null=True)
    _custom_demographics = models.CharField(max_length=2048, null=True)

    @property
    def custom_demographics(self):
        if self._custom_demographics:
            return json.loads(self._custom_demographics)
        return []

    @classmethod
    def retrieve(cls, data):
        data = collections.defaultdict(str, data)
        patient, _ = cls.objects.update_or_create(id=data['id'], first_name=data['first_name'],
            last_name=data['last_name'], doctor_id=data['doctor'],
            _custom_demographics=data['custom_demographics'], gender=data['gender'])
        
        return patient

class CustomDemographic(models.Model):
    id = models.IntegerField(primary_key=True)
    name = models.CharField(max_length=128)
    archived = models.NullBooleanField()
    doctor = models.ForeignKey('Doctor')
    template_name = models.CharField(max_length=128, null=True)
    _allowed_values = models.CharField(max_length=2048, null=True)
    description = models.CharField(max_length=2048, null=True)

    @property
    def allowed_values(self):
        if self._allowed_values:
            return ast.literal_eval(self._allowed_values)
        return []

    @classmethod
    def retrieve(cls, data):
        custom_demographic, _ = cls.objects.update_or_create(id=data['id'], name=data['name'],
            archived=data['archived'], doctor_id=data['doctor'], template_name=data['template_name'],
            _allowed_values=data['allowed_values'], description=data['description'])
        
        return custom_demographic 

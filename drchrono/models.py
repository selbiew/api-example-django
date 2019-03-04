import datetime
import json
from django.db import models
from django.utils.timezone import make_aware

class Appointment(models.Model):
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
    
    id = models.IntegerField(primary_key=True)
    doctor = models.ForeignKey('Doctor')
    duration = models.IntegerField()
    office = models.ForeignKey('Office')
    _exam_room = models.IntegerField()
    patient = models.ForeignKey('Patient')
    reason = models.CharField(max_length=1024)
    scheduled_start_datetime = models.DateTimeField()
    checkin_datetime = models.DateTimeField(null=True)
    start_datetime = models.DateTimeField(null=True)
    status = models.CharField(choices=STATUS_CHOICES, max_length=64, null=True)
    is_walk_in = models.NullBooleanField()
    # recurring_appointsment
    # base_recurring_appointment

    @property
    def scheduled_end_datetime(self):
        if self.scheduled_start_datetime and self.duration:
            return self.scheduled_start_datetime + datetime.timedelta(minutes=float(self.duration))
        return None

    @property
    def scheduled_start_time(self):
        if self.scheduled_start_datetime:
            return self.scheduled_start_datetime.time().strftime('%I:%M %p')
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
        return json.loads(self._exam_rooms)

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
    
    @classmethod
    def retrieve(cls, data):
        patient, _ = cls.objects.update_or_create(id=data['id'], first_name=data['first_name'],
            last_name=data['last_name'], doctor_id=data['doctor'],
            gender=data['gender'])
        
        return patient  

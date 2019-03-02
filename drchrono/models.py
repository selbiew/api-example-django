from django.db import models

class Appointment(models.Model):
    id = models.IntegerField(primary_key=True)
    doctor = models.ForeignKey('Doctor')
    duration = models.IntegerField()
    # Exam_room
    # Office
    patient = models.ForeignKey('Patient')
    scheduled_time = models.DateTimeField()
    # STatus
    # iswalkin
    # recurring_appointsment

    @classmethod
    def retrieve(cls, data):
        appointment, _ = cls.objects.update_or_create(id=data['id'], doctor_id=data['doctor'],
        duration=data['duration'], patient_id=data['patient'], scheduled_time=data['scheduled_time'])

        return appointment  

class AppointmentProfile(models.Model):
    id = models.IntegerField(primary_key=True)
    doctor = models.ForeignKey('Doctor')
    duration = models.IntegerField()
    # Exam_room
    # Office
    name = models.CharField(max_length=64)
    # STatus
    # iswalkin
    # recurring_appointsment

    @classmethod
    def retrieve(cls, data):
        appointment_profile, _ = cls.objects.update_or_create(id=data['id'], doctor_id=data['doctor'],
        duration=data['duration'], name=data['name'])

        return appointment_profile 

class Patient(models.Model):
    GENDER_CHOICES = (
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    )
    id = models.IntegerField(primary_key=True)
    # Date of Birth
    doctor = models.ForeignKey('Doctor')
    gender = models.CharField(choices=GENDER_CHOICES, max_length=6)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)
    
    @classmethod
    def retrieve(cls, data):
        patient, _ = cls.objects.update_or_create(id=data['id'], first_name=data['first_name'],
            last_name=data['last_name'], doctor_id=data['doctor'], gender=data['gender'])
        
        return patient  

class Doctor(models.Model):
    id = models.IntegerField(primary_key=True)
    first_name = models.CharField(max_length=64)
    last_name = models.CharField(max_length=64)

    @classmethod
    def retrieve(cls, data):
        doctor, _ = cls.objects.update_or_create(id=data['id'], first_name=data['first_name'],
            last_name=data['last_name'])
        
        return doctor  


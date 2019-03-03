import datetime
from collections import defaultdict

from drchrono.models import Appointment, AppointmentProfile, Doctor, Patient, Office
from django.shortcuts import redirect
from django.views.generic import TemplateView
from social_django.models import UserSocialAuth

from drchrono.endpoints import DoctorEndpoint, AppointmentEndpoint, AppointmentProfileEndpoint, PatientEndpoint, OfficeEndpoint


class SetupView(TemplateView):
    """
    The beginning of the OAuth sign-in flow. Logs a user into the kiosk, and saves the token.
    """
    template_name = 'kiosk_setup.html'


class DoctorWelcome(TemplateView):
    """
    The doctor can see what appointments they have today.
    """
    template_name = 'doctor_welcome.html'

    def get_token(self):
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']

        return access_token

    def get_doctor(self):
        """
        Use the token we have stored in the DB to make an API request and get doctor details. If this succeeds, we've
        proved that the OAuth setup is working
        """
        access_token = self.get_token()
        api = DoctorEndpoint(access_token)
        
        return next(api.list())

    def get_appointments(self, doctor_id, date=datetime.date.today(), start=None, end=None):
        """
        Use the token we have stored in the DB to make an API request and get all appointments details.
        """
        access_token = self.get_token()
        api = AppointmentEndpoint(access_token)
        appointments = api.list(params={'id': doctor_id}, date=date, start=start, end=end)

        return list(appointments)

    def get_appointment_profiles(self, doctor_id, date=datetime.date.today(), start=None, end=None):
        """
        Use the token we have stored in the DB to make an API request and get all appointment profiles details.
        """
        access_token = self.get_token()
        api = AppointmentProfileEndpoint(access_token)
        appointments = api.list(params={'id': doctor_id})

        return list(appointments)

    def get_patients(self, doctor_id):
        """
        Use the token we have stored in the DB to make an API request and get all patient details.
        """
        access_token = self.get_token()
        api = PatientEndpoint(access_token)
        appointments = api.list(params={'id': doctor_id})

        return list(appointments)

    def get_offices(self):
        """
        Use the token we have stored in the DB to make an API request and get all office details.
        """
        access_token = self.get_token()
        api = OfficeEndpoint(access_token)
        offices = api.list()

        return list(offices)

    def get_context_data(self, **kwargs):
        kwargs = super(DoctorWelcome, self).get_context_data(**kwargs)
        doctor = self.get_doctor()
        offices = self.get_offices()
        appointments = self.get_appointments(doctor['id'])
        appointment_profiles = self.get_appointment_profiles(doctor['id'])
        patients = self.get_patients(doctor['id'])
        kwargs['doctor'] = Doctor.retrieve(doctor)
        kwargs['offices'] = [Office.retrieve(office) for office in offices]
        kwargs['patients'] = [Patient.retrieve(patient) for patient in patients]
        kwargs['appointments'] = [Appointment.retrieve(appointment) for appointment in appointments]
        kwargs['appointment_profiles'] = [AppointmentProfile.retrieve(appointment_profile) for appointment_profile in appointment_profiles]

        return kwargs


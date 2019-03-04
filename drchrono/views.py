import datetime
from collections import defaultdict

from drchrono.models import Appointment, AppointmentProfile, Doctor, Patient, Office
from django.http import HttpRequest, HttpResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from social_django.models import UserSocialAuth
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from drchrono.endpoints import DoctorEndpoint, AppointmentEndpoint, AppointmentProfileEndpoint, PatientEndpoint, OfficeEndpoint

class LoginView(TemplateView):
    """
    The beginning of the OAuth sign-in flow. Logs a user into the kiosk, and saves the token.
    """
    template_name = 'login.html'
    def get(self, request):
        if request.user.is_authenticated:
            if request.GET['next']:
                return redirect(request.GET['next'])
            return redirect('/kiosk')
        return render(request, self.template_name,
            context={'title': 'Kiosk - Setup', 'message_type': 'warning'})

    def post(self, request):
        context = {}
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            if request.GET['next']:
                return redirect(request.GET['next'])
            return redirect('/kiosk', context={"title": "Kiosk - Check In"})
        else:
            context['title'] = 'Kiosk - Setup'
            context['color'] = 'red'
            context['state'] = 'error'
            context['message_type'] = 'error'
            context['header'] = 'Failure'
            context['message'] = 'Unable to log in with that information, please try again.'
        
        return render(request, self.template_name, context=context)

class LogoutView(TemplateView):
    template_name='login.html'

    def get(self, request):
        return redirect('/login', context={'message_type': 'warning'})

    def post(self, request):
        if request.user.is_authenticated:
            logout(request)
        
        return render(request, self.template_name, context={'message_type': 'warning'})

class KioskView(TemplateView):
    template_name = "kiosk.html"

    def get(self, request):
        context = {'title': 'Kiosk - Check In', 'message_type': 'warning'}
        return render(request, self.template_name, context=context)

    def post(self, request):
        context = {'title': 'Kiosk - Check In', 'message_type': 'warning'}
        patient = self.validate_patient(request.POST['first_name'], request.POST['last_name'],
            request.POST['ssn'])
        if patient:
            context['color'] = 'green'
            context['state'] = 'success'
            context['message_type'] = 'success'
            context['header'] = 'Success'
            context['message'] = 'Successfully checked in {last_name}, {first_name}!'.format(
                last_name=request.POST['last_name'],
                first_name=request.POST['first_name'])
        else:
            context['color'] = 'red'
            context['state'] = 'error'
            context['message_type'] = 'error'
            context['header'] = 'Failure'
            context['message'] = 'Unable to check in {last_name}, {first_name}, please try again.'.format(
                last_name=request.POST['last_name'],
                first_name=request.POST['first_name'])
        

        return render(request, self.template_name, context=context)

    def get_token(self):
        """
        Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
        already signed in.
        """
        oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
        access_token = oauth_provider.extra_data['access_token']

        return access_token

    def validate_patient(self, first_name, last_name, ssn):
        access_token = self.get_token()
        api = PatientEndpoint(access_token)
        patients = api.list(params={'first_name': first_name, 'last_name': last_name})
        for patient in patients:
            if patient['social_security_number'][-4:] == ssn:
                return Patient(patient)

        print([patient for patient in patients])
        return None

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
import datetime
from collections import defaultdict

import drchrono.serializers as serializers
from drchrono.models import Appointment, AppointmentProfile, Doctor, Patient, Office, CustomDemographic
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from social_django.models import UserSocialAuth
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from drchrono.endpoints import DoctorEndpoint, AppointmentEndpoint, AppointmentProfileEndpoint, PatientEndpoint, OfficeEndpoint, CustomDemographicEndpoint

    # class SetupView(TemplateView):
    #     template_name = 'kiosk_setup.html'

class LoginView(TemplateView):
    """
    The beginning of the OAuth sign-in flow. Logs a user into the kiosk, and saves the token.
    """
    template_name = 'login.html'
    def get(self, request):
        if request.user.is_authenticated:
            if 'next' in request.GET:
                return redirect(request.GET['next'])
            return redirect('/kiosk')
        return render(request, self.template_name,
            context={'title': 'Kiosk - Setup', 'message_type': 'warning'})

    def post(self, request):
        context = {}
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            if 'next' in request.GET:
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
        
        return redirect('/login', context={'message_type': 'warning'})

class KioskView(TemplateView):
    template_name = "kiosk.html"

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

    def get(self, request):
        context = {'title': 'Kiosk - Check In', 'message_type': 'warning'}

        return render(request, self.template_name, context=context)

    def post(self, request):
        context = {'title': 'Kiosk - Check In', 'message_type': 'warning'}
        if request.POST['appointment_type'] == 'drop_in':
            pass
        elif request.POST['appointment_type'] == 'scheduled':
            patient = self.validate_patient(request.POST['first_name'], request.POST['last_name'],
                request.POST['ssn'])
            if patient:
                return redirect('/patient/?id={id}'.format(id=patient.id))
            else:
                context['color'] = 'red'
                context['state'] = 'error'
                context['message_type'] = 'error'
                context['header'] = 'Failure'
                context['message'] = 'Unable to check in {last_name}, {first_name}, please try again.'.format(
                    last_name=request.POST['last_name'],
                    first_name=request.POST['first_name'])  

        return render(request, self.template_name, context=context)

    def validate_patient(self, first_name, last_name, ssn):
        token = self.get_token()
        api = PatientEndpoint(token)
        patients = api.list(params={'first_name': first_name, 'last_name': last_name})
        for patient in patients:
            if patient['social_security_number'][-4:] == ssn:
                return serializers.Patient.get(patient['id'], token, shallow=False, data=patient)

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

    def get_context_data(self, **kwargs):
        
        kwargs = super(DoctorWelcome, self).get_context_data(**kwargs)
        token = self.get_token()
        doctor = self.get_doctor()
        appointments = self.get_appointments(doctor['id'])

        doctor = serializers.Doctor.get(doctor['id'], token)
        appointments = [serializers.Appointment.get(a['id'], token, shallow=False, data=a) for a in appointments]
        
        kwargs['doctor'] = doctor
        kwargs['appointments'] = appointments
        
        for appointment in appointments:
            print(appointment)

        return kwargs

class PatientView(TemplateView):
    
    def get(self, request):
        id = request.GET['id']
        context = {'title': 'Patient Information', 'message_type': 'warning'}
        token = self.get_token()
        patient = serializers.Patient.get(id, token, shallow=False)
        context['patient'] = patient

        return render(request, 'patient.html', context=context)

    def post(self, request):
        context = {}
        token = self.get_token()
        api = PatientEndpoint(token)
        patient = serializers.Patient.get(request.POST['id'], token, shallow=False)
        data = {key: request.POST[key] for key in request.POST if key in patient.__dict__ and key != 'id'}

        response = api.update(id=request.POST['id'], data=data)

        if not response:
            context['color'] = 'green'
            context['state'] = 'success'
            context['message_type'] = 'success'
            context['header'] = 'Success'
            context['message'] = 'Successfully checked in {last_name}, {first_name}!'.format(
                last_name=patient.last_name,
                first_name=patient.first_name)
        else:
            context['color'] = 'red'
            context['state'] = 'error'
            context['message_type'] = 'error'
            context['header'] = 'Failure'
            context['message'] = 'Unable to check in {last_name}, {first_name}, please try again.'.format(
                last_name=patient.last_name,
                first_name=patient.first_name)

        return render(request, 'kiosk.html', context=context)

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
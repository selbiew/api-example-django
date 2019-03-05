import datetime
from collections import defaultdict

import drchrono.serializers as serializers
from django.conf import settings
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.db.models import Q
from django.shortcuts import redirect, render
from django.views.generic import TemplateView
from social_django.models import UserSocialAuth
from django.utils.decorators import method_decorator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required

from drchrono.models import AppointmentMeta
from drchrono.endpoints import DoctorEndpoint, AppointmentEndpoint, CustomAppointmentFieldEndpoint, PatientEndpoint, OfficeEndpoint

    # class SetupView(TemplateView):
    #     template_name = 'kiosk_setup.html'

def get_token():
    """
    Social Auth module is configured to store our access tokens. This dark magic will fetch it for us if we've
    already signed in.
    """
    oauth_provider = UserSocialAuth.objects.get(provider='drchrono')
    access_token = oauth_provider.extra_data['access_token']

    return access_token

def get_doctor():
    """
    Use the token we have stored in the DB to make an API request and get doctor details. If this succeeds, we've
    proved that the OAuth setup is working
    """
    access_token = get_token()
    api = DoctorEndpoint(access_token)
    
    return next(api.list())

def get_appointments(doctor_id, date=datetime.date.today(), start=None, end=None):
    """
    Use the token we have stored in the DB to make an API request and get all appointments details.
    """
    access_token = get_token()
    api = AppointmentEndpoint(access_token)
    appointments = api.list(params={'id': doctor_id}, date=date, start=start, end=end)

    return list(appointments)

class LoginView(TemplateView):
    """
    The beginning of the OAuth sign-in flow. Logs a user into the kiosk, and saves the token.
    """
    template_name = 'login.html'
    def get(self, request):
        if request.user.is_authenticated:
            if 'next' in request.GET:
                return redirect(request.GET['next'])
            return redirect('/kiosk/')
        return render(request, self.template_name,
            context={'title': 'Kiosk - Setup', 'message_type': 'warning'})

    def post(self, request):
        context = {}
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user:
            login(request, user)
            if 'next' in request.GET:
                return redirect(request.GET['next'])
            return redirect('/kiosk/', context={"title": "Kiosk - Check In"})
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


    def get(self, request):
        context = {'title': 'Kiosk - Check In', 'message_type': 'warning'}
        if 'state' in request.GET:
            state = request.GET['state']
            if state == 'success':
                context['color'] = 'green'
                context['state'] = 'success'
                context['message_type'] = 'success'
                context['header'] = 'Success'
                context['message'] = 'Thanks for checking in!'
            elif state == 'failure':
                context['color'] = 'red'
                context['state'] = 'error'
                context['message_type'] = 'error'
                context['header'] = 'Failure'
                context['message'] = 'Unable to check in, please try again.' 

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
        token = get_token()
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

    def get(self, request):   
        context = {}
        
        try:
            token = get_token()
            doctor = get_doctor()
            appointments = get_appointments(doctor['id'])

            doctor = serializers.Doctor.get(doctor['id'], token)
            appointments = [serializers.Appointment.get(a['id'], token, shallow=False, data=a) for a in appointments]

            context['doctor'] = doctor
            context['appointments'] = appointments
        except:
            pass

        today_min = datetime.datetime.combine(datetime.date.today(), datetime.time.min)
        today_max = datetime.datetime.combine(datetime.date.today(), datetime.time.max)
        todays_appointments = AppointmentMeta.objects.filter(Q(arrival_time__range=(today_min, today_max)) | Q(start_time__range=(today_min, today_max)))
        completed_appointments = todays_appointments.filter(start_time__range=(today_min, today_max))
        
        if todays_appointments:
            total_wait_time = sum([a.wait_time for a in todays_appointments])
            average_wait_time = total_wait_time / len(todays_appointments)

            context['total_wait_time'] = int(total_wait_time)
            context['average_wait_time'] = int(average_wait_time)
        if completed_appointments:
            context['patient_count'] = len(completed_appointments)

        return render(request, self.template_name, context=context)

    def post(self, request):
        patient_id = request.POST['patient_id']
        appointment_id = request.POST['appointment_id']
        doctor_id = request.POST['doctor_id']

        token = get_token()
        appointment_api = AppointmentEndpoint(token)
        appointments = appointment_api.list(params={'doctor': doctor_id}, date=datetime.datetime.now())
        for appointment in appointments:
            if appointment['status'] == 'In Session':
                appointment_api.update(appointment['id'], data={'status': 'Complete'})
            elif appointment_id == appointment['id'] and appointment['status'] in ['Arrived', 'Checked In', 'In Room']:
                appointment_api.update(appointment_id, data={'status': 'In Session'})
                a, _ = AppointmentMeta.objects.get_or_create(id=appointment['id'])
                a.start_time = datetime.datetime.now()
                a.save()

        return redirect('/welcome/')

class PatientView(TemplateView):
    
    def get(self, request):
        if 'id' in request.GET:
            id = request.GET['id']
        else:
            return redirect('/kiosk/?state=failure')
        context = {'title': 'Patient Information', 'message_type': 'warning'}
        token = get_token()
        patient = serializers.Patient.get(id, token, shallow=False)
        context['patient'] = patient

        return render(request, 'patient.html', context=context)

    def post(self, request):
        token = get_token()
        
        patient_api = PatientEndpoint(token)
        patient = serializers.Patient.get(request.POST['id'], token, shallow=False)
        data = {key: request.POST[key] for key in request.POST if key in patient.__dict__ and key != 'id'}

        patient_response = patient_api.update(id=request.POST['id'], data=data)

        if not patient_response:
            appointment_api = AppointmentEndpoint(token)
            appointments = list(appointment_api.list(params={'patient': patient.id}, date=datetime.datetime.today()))

            if appointments:
                appointments = [serializers.Appointment.get(a['id'], token, shallow=False, data=a) for a in appointments]

                deltas = [(a.id, abs(datetime.datetime.now() - a.scheduled_start_datetime)) for a in appointments]
                deltas.sort(key=lambda t: t[1])

                appointment_api.update(deltas[0][0], data={'status': 'Arrived'})
                a, created = AppointmentMeta.objects.get_or_create(id=deltas[0][0])

                if created:
                    a.arrival_time = datetime.datetime.now()
                    a.save()

                return redirect('/kiosk/?state=success')

        return redirect('/kiosk/?state=failure')
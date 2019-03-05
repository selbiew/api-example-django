from django.conf.urls import include, url
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.contrib import admin
admin.autodiscover()

import views

urlpatterns = [
    url(r'^login/$', views.LoginView.as_view(), name='login'),
    url(r'^patient/', views.PatientView.as_view(), name='patient'),
    # url(r'^setup/$', views.SetupView.as_view(), name='setup'),
    url(r'^kiosk/$', login_required(views.KioskView.as_view()), name='kiosk'),
    url(r'^logout/$', views.LogoutView.as_view(), name='logout'),
    url(r'^welcome/$', login_required(views.DoctorWelcome.as_view()), name='welcome'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'', include('social.apps.django_app.urls', namespace='social')),
]
from django.contrib import admin
from django.urls import path, include
from gmsapp.views import *

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('gmsapp.urls')),

]
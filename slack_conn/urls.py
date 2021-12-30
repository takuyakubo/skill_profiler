from django.urls import path
from . import views

urlpatterns = [
                  path('praise', views.mention, name='praise'),
                  path('profile', views.profile, name='profile'),
              ]
from django.urls import path
from . import views

urlpatterns = [
                  path('praise', views.praise, name='praise'),
                  path('profile', views.profile, name='profile'),
              ]
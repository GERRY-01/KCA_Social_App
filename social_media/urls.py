from django.urls import path

from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('signup/', views.signup, name='signup'),
    path('complete_profile/', views.complete_profile, name='complete_profile'),
    path('login/', views.login, name='login'),
    path('create_post/', views.create_post, name='create_post'),
]
from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('accounts/login/', views.login_view, name='login'),
    path('signin/', views.signin_view, name='singin'),
    path('logout/', views.logout_view, name='logout'),
    path('connect/', views.connect_view, name='connect'),
    path('webdev/', views.webdev, name='webdev'),
    path('python/', views.python, name='python'),
    path('datasci/', views.datasci, name='datasci'),
    path('machine/', views.machine, name='machine'),
    path('datatc/', views.datatc, name='datatc'),
    path('sql/', views.sql, name='sql'),
    path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
    path('index1', views.index1, name='index1'),
    path('execute/', views.execute_code, name='execute_code'),
]

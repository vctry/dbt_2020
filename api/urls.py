from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('plot_change/', views.plot_change, name='plot_change'),
    path('plot/', views.plot, name='plot')
]

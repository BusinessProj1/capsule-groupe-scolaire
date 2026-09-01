from django.urls import path
from . import views

urlpatterns = [
    path('', views.index_view, name='index'),
    path('methode/', views.methode_view, name='methode'),
    path('cours/', views.cours_view, name='cours'),
    path('tarifs/', views.tarifs_view, name='tarifs'),
    path('temoignages/', views.temoignages_view, name='temoignages'),
    path('ressources/', views.ressources_view, name='ressources'),
    path('apropos/', views.apropos_view, name='apropos'),
    path('contact/', views.contact_view, name='contact'),
    path('lecon-type/', views.lecon_type_view, name='lecon_type'),
]

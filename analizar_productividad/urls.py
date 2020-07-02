from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('processing', views.main_processing, name='main_processing'),
    path('upload/', views.upload_file, name='upload_file'),
    ]

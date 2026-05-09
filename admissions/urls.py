from django.urls import path
from . import views

app_name = 'admissions'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('records/', views.admission_list, name='admission_list'),
    path('records/new/', views.admission_create, name='admission_create'),
    path('records/<int:pk>/', views.admission_detail, name='admission_detail'),
    path('records/<int:pk>/edit/', views.admission_edit, name='admission_edit'),
    path('records/<int:pk>/delete/', views.admission_delete, name='admission_delete'),
    path('export/detailed/', views.export_detailed_excel, name='export_detailed'),
    path('export/summary/', views.export_summary_excel, name='export_summary'),
]

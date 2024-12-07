from django.urls import path
from webapp import views

urlpatterns = [
    path('', views.app, name='app'),
    path('stream/', views.stream, name='stream'),
    path('admin_dashboard/', views.indexadmin, name='admin_dashboard'),
    path('academic_year/', views.academic_year_view, name='academic_year'),
    path('division/', views.division_view, name='division'),
    path('classes/', views.classes_view, name='classes'),
    path('students/', views.students_view, name='students'),
    path('attendance/', views.attendance_view, name='attendance'),
    path('send_attendance_email/', views.send_attendance_email, name='send_attendance_email'),
    path('send-email/', views.send_email_to_teachers, name='send_email_to_teachers'),
    path('admin/', views.admin_login, name='admin_login'),
    ]

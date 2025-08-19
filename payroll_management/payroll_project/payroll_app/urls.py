from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view, name='login'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('add_meeting/', views.add_meeting, name='add_meeting'),
    path('employees/', views.employees_view, name='employees'),

    # Employee CRUD
    path('employees/add/', views.add_employee_view, name='add_employee'),
    path('employees/edit/<int:id>/', views.edit_employee_view, name='edit_employee'),
    path('employees/delete/<int:id>/', views.delete_employee_view, name='delete_employee'),

    # Payroll & Payslip
    path('payroll/', views.payroll_view, name='payroll'),
    path('payslip/', views.payslip_view, name='payslip'),
    path("payslip/<int:employee_id>/download/", views.download_payslip, name="download_payslip"),

    # Upgrade (only one path!)
    path("upgrade/", views.upgrade_view, name="upgrade"),
    path("upgrade/premium/", views.upgrade_premium, name="upgrade_premium"),
    
    # Logout
    path('logout/', views.logout_view, name='logout'),
]

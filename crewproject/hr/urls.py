
from django.urls import path

from hr import views

urlpatterns = [path('',views.login_view,name='login'),
               path("dashboard/",views.dashboard, name="dashboard"),
               path("logout/",views.logout_view, name="logout"),
               # path("viewemployees/", viewemployees, name="viewemployees"),
               #employee related urls
               path('employees/',views.employee_list,name="employee_list"),
               path('employees/add/',views.employee_create,name="employee_create"),
               path("employees/<int:id>/edit/", views.employee_update, name="employee_update"),
               path("employees/<int:id>/delete/", views.employee_delete, name="employee_delete"),
               path("leave_approve/",views.leave_approve, name="leave_approve"),
               path("leave/<int:id>/action/",views.leave_action, name="leave_action"),
               path("payroll/",views.payrolls, name="payroll"),
               path("payroll/<int:employee_id>/", views.payroll_details, name="payroll_details"),
               path("reports/",views.reports,name="reports"),
               path("department/",views.departments,name="department"),
               path("add_department",views.add_department,name="add_department"),
               path("departments/edit/<int:department_id>/", views.edit_department, name="edit_department"),
               path("departments/delete/<int:department_id>/",views.delete_department,name="delete_department"),
               path("designations/",views.designations,name="designations"),
               path("add_designation/",views.add_designation,name="add_designation"),
               path("edit_designation/<int:id>/",views.edit_designation, name="edit_designation" ),
               path("delete_designation/<int:id>/",views.delete_designation,name="delete_designation"),
               path("settings/",views.settings_view,name="settings"),
               path("view_profile/",views.view_profile,name="view_profile"),
               path("change_password/",views.change_password,name="change_password"),
               ]
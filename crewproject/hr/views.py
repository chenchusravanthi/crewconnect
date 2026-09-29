from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from hr.models import Employee, Department, Designation, Leave

from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.core.mail import send_mail




def login_view(request):

    if request.method == "POST":

        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request, user)
            if Employee.objects.filter(user=user).exists():
                return redirect("employee_dashboard")
            return redirect("dashboard")
        return render(request,"login.html",{"error": "Invalid username or password"})
    return render(request, "login.html")



@login_required
@never_cache
def dashboard(request):
    return render(request, "dashboard.html")


def logout_view(request):
    logout(request)
    return redirect("login")

@login_required()
@never_cache
def employee_list(request):
    employees=(Employee.objects.select_related("department","designation").filter(status=True))
    return render(request, "employee_list.html", {"employees":employees})

login_required()
@never_cache
def employee_create(request):

    departments = Department.objects.all()
    designations = Designation.objects.all()

    if request.method == "POST":

        employee_id = request.POST.get("employee_id")
        name = request.POST.get("name")
        email = request.POST.get("email")
        phone = request.POST.get("phone")

        department_id = request.POST.get("department")
        designation_id = request.POST.get("designation")

        joining_date = request.POST.get("joining_date")
        employment_type = request.POST.get("employment_type")
        salary = request.POST.get("salary")
        address = request.POST.get("address")

        status = request.POST.get("status") == "on"
        if Employee.objects.filter(email=email).exists():
            messages.error(
                request,
                "Employee with this email already exists."
            )
            return redirect("employee_create")

        # Create Django User
        user = User.objects.create_user(
            username=email,
            email=email,
            first_name=name
        )

        # Disable password until employee creates one
        user.set_unusable_password()
        user.save()

        # Create Employee
        employee = Employee.objects.create(
            user=user,
            employee_id=employee_id,
            name=name,
            email=email,
            phone=phone,
            department_id=department_id,
            designation_id=designation_id,
            joining_date=joining_date,
            employment_type=employment_type,
            salary=salary,
            address=address,
            status=status
        )

        # Generate password setup token
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Password setup URL
        setup_link = request.build_absolute_uri(
            reverse(
                "set_password",
                kwargs={
                    "uidb64": uid,
                    "token": token
                }
            )
        )

        # Send email
        send_mail(
            subject="CrewConnect - Set Your Password",
            message=f"""
Hello {name},

Your CrewConnect employee account has been created.

Please click the link below to create your password:

{setup_link}

After setting your password, you can log in to CrewConnect.

Regards,
CrewConnect HR
""",
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[email],
        )

        return redirect("employee_list")

    return render(
        request,
        "employee_add_update.html",
        {
            "departments": departments,
            "designations": designations,
            "employment_types": Employee.EMPLOYMENT_TYPES,
            "is_update": False,
        }
    )

@login_required()
@never_cache
def employee_update(request, id):


    employee = get_object_or_404(Employee,id=id)


    departments = Department.objects.all()
    designations = Designation.objects.all()


    if request.method == "POST":


        employee.employee_id = request.POST.get("employee_id")
        employee.name = request.POST.get("name")
        employee.email = request.POST.get("email")
        employee.phone = request.POST.get("phone")


        employee.department_id = request.POST.get("department")
        employee.designation_id = request.POST.get("designation")


        employee.joining_date = request.POST.get("joining_date")
        employee.employment_type = request.POST.get("employment_type")
        employee.salary = request.POST.get("salary")
        employee.address = request.POST.get("address")


        employee.status = request.POST.get("status") == "on"


        employee.save()


        return redirect(
            "employee_list"
        )


    return render(
        request,
        "employee_add_update.html",
        {
            "employee": employee,
            "departments": departments,
            "designations": designations,
            "employment_types": Employee.EMPLOYMENT_TYPES,
            "is_update": True,
        }
    )

@login_required()
@never_cache
def employee_delete(request, id):
    employee = get_object_or_404(
        Employee,
        id=id
    )
    employee.status = not employee.status
    employee.save()
    return redirect("employee_list")


@login_required
def leave_approve(request):


   # Check whether logged-in user is an employee
   if Employee.objects.filter(user=request.user).exists():
       return redirect("employee_dashboard")


   leaves = Leave.objects.select_related(
       "employee",
       "employee__department",
       "employee__designation"
   ).order_by("-applied_date")


   return render(
       request,
       "leave_approval.html",
       {
           "leaves": leaves,
           "is_employee": False,
       }
   )




@login_required
def leave_action(request, id):


    # Employee cannot approve/reject
    if Employee.objects.filter(user=request.user).exists():
        return redirect("employee_dashboard")


    if request.method == "POST":


        leave = Leave.objects.get(id=id)


        action = request.POST.get("action")


        if action == "approve":


            leave.status = "Approved"
            leave.save()


        elif action == "reject":


            leave.status = "Rejected"
            leave.save()


    return redirect("leave_approve")


@login_required
def payrolls(request):

    employees = Employee.objects.filter(
        status=True
    ).select_related(
        "department",
        "designation"
    ).order_by("employee_id")

    return render(
        request,
        "hr_payroll.html",
        {
            "employees": employees
        }
    )


@login_required
def payroll_details(request, employee_id):

    employee = Employee.objects.get(id=employee_id)

    return render(
        request,
        "hr_payroll_details.html",
        {
            "employee": employee
        }
    )
@login_required
def reports(request):

    # Employee counts
    total_employees = Employee.objects.count()

    active_employees = Employee.objects.filter(
        status=True
    ).count()

    inactive_employees = Employee.objects.filter(
        status=False
    ).count()

    # Employment type counts
    permanent_employees = Employee.objects.filter(
        employment_type="Permanent"
    ).count()

    contract_employees = Employee.objects.filter(
        employment_type="Contract"
    ).count()

    part_time_employees = Employee.objects.filter(
        employment_type="Part-time"
    ).count()

    intern_employees = Employee.objects.filter(
        employment_type="Intern"
    ).count()

    # Department count
    total_departments = Department.objects.count()

    # Leave counts
    total_leaves = Leave.objects.count()

    pending_leaves = Leave.objects.filter(
        status="Pending"
    ).count()

    approved_leaves = Leave.objects.filter(
        status="Approved"
    ).count()

    rejected_leaves = Leave.objects.filter(
        status="Rejected"
    ).count()

    # Recent employee records
    employees = Employee.objects.select_related(
        "department",
        "designation"
    ).order_by("employee_id")

    context = {
        "total_employees": total_employees,
        "active_employees": active_employees,
        "inactive_employees": inactive_employees,

        "permanent_employees": permanent_employees,
        "contract_employees": contract_employees,
        "part_time_employees": part_time_employees,
        "intern_employees": intern_employees,

        "total_departments": total_departments,

        "total_leaves": total_leaves,
        "pending_leaves": pending_leaves,
        "approved_leaves": approved_leaves,
        "rejected_leaves": rejected_leaves,

        "employees": employees,
    }

    return render(
        request,
        "hr_reports.html",
        context
    )


@login_required
def departments(request):

    departments = Department.objects.all().order_by("name")

    for department in departments:
        department.employee_count = Employee.objects.filter(
            department=department
        ).count()

    return render(request, "hr_departments.html",{"departments": departments }  )


@login_required
def add_department(request):

    if request.method == "POST":

        name = request.POST.get("name", "").strip()

        if not name:
            messages.error(
                request,
                "Department name is required."
            )

        elif Department.objects.filter( name__iexact=name).exists():

            messages.error(request,"Department already exists.")

        else:

            Department.objects.create(name=name)

            messages.success(request,"Department added successfully." )

            return redirect("department")

    return render(request,"hr_add_department.html")


@login_required
def edit_department(request, department_id):

    department = get_object_or_404(
        Department,
        id=department_id
    )

    if request.method == "POST":

        name = request.POST.get("name", "").strip()

        if not name:

            messages.error(
                request,
                "Department name is required."
            )

        elif Department.objects.filter(
            name__iexact=name
        ).exclude(
            id=department.id
        ).exists():

            messages.error(
                request,
                "Department already exists."
            )

        else:

            department.name = name
            department.save()

            messages.success(
                request,
                "Department updated successfully."
            )

            return redirect("department")

    return render(
        request,
        "hr_edit_department.html",
        {
            "department": department
        }
    )


@login_required
def delete_department(request, department_id):

    department = get_object_or_404(
        Department,
        id=department_id
    )

    # Check whether employees belong to this department
    employee_count = Employee.objects.filter(
        department=department
    ).count()

    if employee_count > 0:

        messages.error(
            request,
            "This department cannot be deleted because employees are assigned to it."
        )

    else:

        department.delete()

        messages.success(
            request,
            "Department deleted successfully."
        )

    return redirect("department")


def designations(request):
    designation_list = Designation.objects.all().order_by('id')

    return render(request, "designations.html", {
        "designations": designation_list
    })


def add_designation(request):
    if request.method == "POST":
        name = request.POST.get("name")

        if not name:
            messages.error(request, "Designation name is required.")
            return redirect("add_designation")

        if Designation.objects.filter(name__iexact=name).exists():
            messages.error(request, "Designation already exists.")
            return redirect("add_designation")

        Designation.objects.create(
            name=name
        )

        messages.success(request, "Designation added successfully.")

        return redirect("designations")

    return render(request, "add_designation.html")


def edit_designation(request, id):

    designation = get_object_or_404(Designation, id=id)

    if request.method == "POST":

        name = request.POST.get("name")
        description = request.POST.get("description")

        if not name:
            messages.error(request, "Designation name is required.")
            return redirect("edit_designation", id=id)

        if Designation.objects.filter(
            name__iexact=name
        ).exclude(id=id).exists():

            messages.error(request, "Designation already exists.")
            return redirect("edit_designation", id=id)

        designation.name = name
        designation.description = description
        designation.save()

        messages.success(
            request,
            "Designation updated successfully."
        )

        return redirect("designations")

    return render(request, "edit_designation.html", {
        "designation": designation
    })


def delete_designation(request, id):

    designation = get_object_or_404(Designation, id=id)

    designation.delete()

    messages.success(
        request,
        "Designation deleted successfully."
    )

    return redirect("designations")

@login_required
def settings_view(request):
    return render(request, "settings.html")

@login_required
def view_profile(request):

    employee = Employee.objects.filter(
        user=request.user
    ).first()

    if employee is None:
        messages.error(
            request,
            "Your account is not linked to an employee profile."
        )
        return redirect("settings")

    return render(request, "view_profile.html", {
        "employee": employee
    })

@login_required
def change_password(request):

    if request.method == "POST":

        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Check old password
        if not request.user.check_password(old_password):
            messages.error(
                request,
                "Current password is incorrect."
            )
            return redirect("change_password")

        # Check new passwords
        if new_password != confirm_password:
            messages.error(
                request,
                "New passwords do not match."
            )
            return redirect("change_password")

        # Check password length
        if len(new_password) < 8:
            messages.error(
                request,
                "Password must contain at least 8 characters."
            )
            return redirect("change_password")

        # Change password
        request.user.set_password(new_password)
        request.user.save()

        # Keep user logged in
        update_session_auth_hash(
            request,
            request.user
        )

        messages.success(
            request,
            "Password changed successfully."
        )

        return redirect("settings")

    return render(
        request,
        "change_password.html"
    )
# payroll_app/views.py
from datetime import datetime
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.timezone import now, make_aware
from .models import Employee, Meeting
from .forms import EmployeeForm
from xhtml2pdf import pisa
import io
from django.contrib import messages

MONTHS = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]

FREE_TEMPLATES = getattr(settings, "FREE_TEMPLATES", [
    "payroll_app/payslip_template1.html",
    "payroll_app/payslip_template2.html",
    "payroll_app/payslip_template3.html",
])

PREMIUM_TEMPLATES = getattr(settings, "PREMIUM_TEMPLATES", [
    "payroll_app/payslip_template4.html",
    "payroll_app/payslip_template5.html",
])


# ---------------- LOGIN ----------------
def login_view(request):
    if request.user.is_authenticated:
        return redirect("dashboard")
    error = None
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        if not username or not password:
            error = "Username and password are required."
        else:
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect("dashboard")
            error = "Invalid username or password."
    return render(request, "payroll_app/login.html", {"error": error})


# ---------------- DASHBOARD ----------------
@login_required
def dashboard_view(request):
    today = now()
    current_month = today.strftime("%B %Y")

    employees = Employee.objects.all()
    total_employees = employees.count()
    hired_candidates = Employee.objects.filter(
        join_date__year=today.year, join_date__month=today.month
    ).count()
    net_salary_total = sum(emp.net_salary for emp in employees)

    employee_names = [emp.name for emp in employees]
    employee_salaries = [float(emp.net_salary) for emp in employees]

    meetings = Meeting.objects.filter(
        meeting_time__month=today.month,
        meeting_time__year=today.year,
    )

    meetings_by_date = {}
    for m in meetings:
        date_str = m.meeting_time.date().isoformat()
        meetings_by_date.setdefault(date_str, []).append(m.meeting_info)

    context = {
        "current_month": current_month,
        "total_employees": total_employees,
        "hired_candidates": hired_candidates,
        "net_salary_total": float(net_salary_total),
        "employee_names": employee_names,
        "employee_salaries": employee_salaries,
        "meetings_by_date": meetings_by_date,
    }
    return render(request, "payroll_app/dashboard.html", context)


# ---------------- MEETINGS ----------------
@login_required
def add_meeting(request):
    if request.method == "POST":
        meeting_time_str = request.POST.get("meeting_time", "").strip()
        meeting_info = request.POST.get("meeting_info", "").strip()

        if not meeting_time_str:
            messages.error(request, "Meeting time is required.")
            return redirect("dashboard")
        if not meeting_info:
            messages.error(request, "Meeting details are required.")
            return redirect("dashboard")

        try:
            meeting_time = make_aware(datetime.fromisoformat(meeting_time_str))
        except (ValueError, TypeError):
            messages.error(request, "Invalid meeting time format.")
            return redirect("dashboard")

        Meeting.objects.create(meeting_time=meeting_time, meeting_info=meeting_info)
        messages.success(request, "Meeting added successfully.")
    return redirect("dashboard")


# ---------------- EMPLOYEE CRUD ----------------
@login_required
def employees_view(request):
    employees = Employee.objects.all()
    return render(request, "payroll_app/employees.html", {"employees": employees})


@login_required
def add_employee_view(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee added successfully.")
            return redirect("employees")
    else:
        form = EmployeeForm()
    return render(request, "payroll_app/employee_form.html", {"form": form, "title": "Add Employee"})


@login_required
def edit_employee_view(request, id):
    employee = get_object_or_404(Employee, id=id)
    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            messages.success(request, "Employee updated successfully.")
            return redirect("employees")
    else:
        form = EmployeeForm(instance=employee)
    return render(request, "payroll_app/employee_form.html", {"form": form, "title": "Edit Employee"})


@login_required
def delete_employee_view(request, id):
    employee = get_object_or_404(Employee, id=id)
    if request.method == "POST":
        employee.delete()
        messages.success(request, "Employee deleted successfully.")
        return redirect("employees")
    return render(request, "payroll_app/employee_confirm_delete.html", {"employee": employee})


# ---------------- PAYROLL ----------------
@login_required
def payroll_view(request):
    employees_list = Employee.objects.all()
    selected_month = None

    if request.method == "POST":
        month_input = request.POST.get("month", "").strip()
        if month_input in MONTHS:
            selected_month = month_input
        else:
            messages.error(request, "Please select a valid month.")

    employee_data = [
        {
            "id": emp.id,
            "name": emp.name,
            "role": emp.role,
            "salary": float(emp.salary),
            "bonus": float(emp.bonus),
            "deduction": float(emp.deduction),
            "net_salary": float(emp.net_salary),
            "status": "Calculated",
        }
        for emp in employees_list
    ]

    return render(
        request,
        "payroll_app/payroll.html",
        {
            "employees": employee_data,
            "selected_month": selected_month,
            "months": MONTHS,
        },
    )


# ---------------- PAYSLIP ----------------
@login_required
def payslip_view(request):
    employees = Employee.objects.all()
    selected_employee = None
    selected_month = datetime.now().strftime("%B %Y")
    selected_template = FREE_TEMPLATES[0]
    is_premium = False
    allowed_templates = FREE_TEMPLATES

    if request.method == "POST":
        emp_id = request.POST.get("employee", "").strip()
        template_choice = request.POST.get("template_id", "").strip()

        if not emp_id:
            messages.error(request, "Please select an employee.")
        else:
            selected_employee = get_object_or_404(Employee, id=emp_id)
            is_premium = selected_employee.is_premium
            allowed_templates = FREE_TEMPLATES + PREMIUM_TEMPLATES if is_premium else FREE_TEMPLATES

            if template_choice and template_choice.isdigit():
                index = int(template_choice) - 1
                if 0 <= index < len(allowed_templates):
                    selected_template = allowed_templates[index]
                else:
                    selected_template = FREE_TEMPLATES[0]

    return render(request, "payroll_app/payslip.html", {
        "employees": employees,
        "selected_employee": selected_employee,
        "selected_month": selected_month,
        "templates": allowed_templates,
        "selected_template": selected_template,
        "is_premium": is_premium,
    })


@login_required
def download_payslip(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    is_premium = employee.is_premium
    allowed_templates = FREE_TEMPLATES + PREMIUM_TEMPLATES if is_premium else FREE_TEMPLATES

    template_id = request.GET.get("template_id", "1").strip()
    if not template_id.isdigit():
        template_id = "1"

    template_map = {str(i + 1): t for i, t in enumerate(FREE_TEMPLATES + PREMIUM_TEMPLATES)}
    template_name = template_map.get(template_id, FREE_TEMPLATES[0])

    if template_name not in allowed_templates:
        template_name = FREE_TEMPLATES[0]

    html_content = render_to_string(template_name, {"employee": employee})
    result = io.BytesIO()
    pdf = pisa.CreatePDF(io.BytesIO(html_content.encode("UTF-8")), dest=result)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type="application/pdf")
        response["Content-Disposition"] = f'attachment; filename="payslip_{employee.name}.pdf"'
        return response
    return HttpResponse("Error generating PDF.", status=500)


# ---------------- UPGRADE ----------------
@login_required
def upgrade_view(request):
    if request.method == "POST":
        messages.success(request, "Upgrade request received. Premium unlocked!")
        return redirect("payslip")
    return render(request, "payroll_app/upgrade.html")


@login_required
def upgrade_premium(request):
    return render(request, "payroll_app/upgrade_premium.html")


# ---------------- LOGOUT ----------------
def logout_view(request):
    logout(request)
    return redirect("login")

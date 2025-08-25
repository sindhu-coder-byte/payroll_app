# payroll_app/views.py
from datetime import datetime
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.template.loader import render_to_string
from django.utils.timezone import now, make_aware
from .models import Employee, Meeting
from .forms import EmployeeForm
from xhtml2pdf import pisa
import io
from django.contrib import messages


# ---------------- LOGIN ----------------
def login_view(request):
    error = None
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect("dashboard")
        error = "Invalid username or password"
    return render(request, "payroll_app/login.html", {"error": error})


# ---------------- DASHBOARD ----------------
def dashboard_view(request):
    today = now()
    current_month = today.strftime("%B %Y")

    employees = Employee.objects.all()
    total_employees = employees.count()
    hired_candidates = Employee.objects.filter(
        join_date__year=today.year, join_date__month=today.month
    ).count()
    net_salary_total = sum([emp.net_salary for emp in employees])

    employee_names = [emp.name for emp in employees]
    employee_salaries = [float(emp.net_salary) for emp in employees]

    meetings = Meeting.objects.filter(
    meeting_time__month=today.month,
    meeting_time__year=today.year
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
def add_meeting(request):
    if request.method == "POST":
        meeting_time_str = request.POST.get("meeting_time")
        meeting_info = request.POST.get("meeting_info")

        if meeting_time_str and meeting_info:
            meeting_time = make_aware(datetime.fromisoformat(meeting_time_str))
            Meeting.objects.create(meeting_time=meeting_time, meeting_info=meeting_info)
    return redirect("dashboard")


# ---------------- EMPLOYEE CRUD ----------------
def employees_view(request):
    employees = Employee.objects.all()
    return render(request, "payroll_app/employees.html", {"employees": employees})


def add_employee_view(request):
    if request.method == "POST":
        form = EmployeeForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("employees")
    else:
        form = EmployeeForm()
    return render(request, "payroll_app/employee_form.html", {"form": form, "title": "Add Employee"})


def edit_employee_view(request, id):
    employee = get_object_or_404(Employee, id=id)
    if request.method == "POST":
        form = EmployeeForm(request.POST, instance=employee)
        if form.is_valid():
            form.save()
            return redirect("employees")
    else:
        form = EmployeeForm(instance=employee)
    return render(request, "payroll_app/employee_form.html", {"form": form, "title": "Edit Employee"})


def delete_employee_view(request, id):
    employee = get_object_or_404(Employee, id=id)
    if request.method == "POST":
        employee.delete()
        return redirect("employees")
    return render(request, "payroll_app/employee_confirm_delete.html", {"employee": employee})


# ---------------- PAYROLL ----------------
def payroll_view(request):
    employees_list = Employee.objects.all()
    selected_month = request.POST.get("month") if request.method == "POST" else None

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
            "months": [
                "January","February","March","April","May","June",
                "July","August","September","October","November","December"
            ],
        },
    )


# ---------------- PAYSLIP ----------------
# Default free templates
FREE_TEMPLATES = getattr(settings, "FREE_TEMPLATES", [
    "payroll_app/payslip_template1.html",
    "payroll_app/payslip_template2.html",
    "payroll_app/payslip_template3.html",
])

# Premium templates
PREMIUM_TEMPLATES = getattr(settings, "PREMIUM_TEMPLATES", [
    "payroll_app/payslip_template4.html",
    "payroll_app/payslip_template5.html",
])

FREE_TEMPLATES = getattr(settings, "FREE_TEMPLATES", [
    "payroll_app/payslip_template1.html",
    "payroll_app/payslip_template2.html",
    "payroll_app/payslip_template3.html",
])

PREMIUM_TEMPLATES = getattr(settings, "PREMIUM_TEMPLATES", [
    "payroll_app/payslip_template4.html",
    "payroll_app/payslip_template5.html",
])

def payslip_view(request):
    employees = Employee.objects.all()
    selected_employee = None
    selected_month = datetime.now().strftime("%B %Y")
    selected_template = FREE_TEMPLATES[0]

    if request.method == "POST":
        emp_id = request.POST.get("employee")
        template_choice = request.POST.get("template_id")

        if emp_id:
            selected_employee = get_object_or_404(Employee, id=emp_id)

        # Use employee's premium status
        is_premium = selected_employee.is_premium if selected_employee else False
        allowed_templates = FREE_TEMPLATES + PREMIUM_TEMPLATES if is_premium else FREE_TEMPLATES

        if template_choice and template_choice.isdigit():
            index = int(template_choice) - 1
            if 0 <= index < len(allowed_templates):
                selected_template = allowed_templates[index]
            else:
                selected_template = FREE_TEMPLATES[0]

    else:
        is_premium = False
        allowed_templates = FREE_TEMPLATES

    return render(request, "payroll_app/payslip.html", {
        "employees": employees,
        "selected_employee": selected_employee,
        "selected_month": selected_month,
        "templates": allowed_templates,
        "selected_template": selected_template,
        "is_premium": is_premium,
    })


def download_payslip(request, employee_id):
    employee = get_object_or_404(Employee, id=employee_id)
    
    # Use employee's premium status
    is_premium = employee.is_premium
    allowed_templates = FREE_TEMPLATES + PREMIUM_TEMPLATES if is_premium else FREE_TEMPLATES

    template_id = request.GET.get("template_id", "1")
    template_map = {str(i+1): t for i, t in enumerate(FREE_TEMPLATES + PREMIUM_TEMPLATES)}
    template_name = template_map.get(template_id, FREE_TEMPLATES[0])

    if template_name not in allowed_templates:
        template_name = FREE_TEMPLATES[0]

    html_content = render_to_string(template_name, {"employee": employee})

    result = io.BytesIO()
    pdf = pisa.CreatePDF(io.BytesIO(html_content.encode("UTF-8")), dest=result)

    if not pdf.err:
        response = HttpResponse(result.getvalue(), content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="payslip_{employee.name}.pdf"'
        return response
    else:
        return HttpResponse("Error generating PDF", status=500)
    

def upgrade_view(request):
    if request.method == "POST":
        # Later integrate Stripe/Razorpay/etc here
        messages.success(request, "Upgrade request received. Premium unlocked!")
        return redirect("payslip")  # redirect back to payslip page
    return render(request, "payroll_app/upgrade.html")
    return redirect('upgrade_premium')

def upgrade_premium(request):
    # You can later connect payment gateway or premium templates here
    return render(request, "upgrade_premium.html")


# ---------------- LOGOUT ----------------
def logout_view(request):
    logout(request)
    return redirect("login")

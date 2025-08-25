from django import forms
from .models import Employee

class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'name', 'role', 'department', 'salary', 'bonus', 'da', 'join_date',
            'work_hours', 'working_days', 'designation', 'leave_days', 
            'deduction', 'status'
        ]
        widgets = {
            'join_date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'px-3 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-[#00b9b9]'
            }),
            'name': forms.TextInput(attrs={
                'class': 'px-3 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-[#00b9b9]'
            }),
            'role': forms.TextInput(attrs={
                'class': 'px-3 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-[#00b9b9]'
            }),
            'department': forms.TextInput(attrs={
                'class': 'px-3 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-[#00b9b9]'
            }),
            'salary': forms.NumberInput(attrs={
                'class': 'px-3 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-[#00b9b9]'
            }),
            'bonus': forms.NumberInput(attrs={
                'class': 'px-3 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-[#00b9b9]'
            }),
            'da': forms.NumberInput(attrs={
                'class': 'px-3 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-[#00b9b9]'
            }),
            'designation': forms.TextInput(attrs={
                'class': 'px-3 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-[#00b9b9]'
            }),
            'work_hours': forms.NumberInput(attrs={
                'class': 'px-3 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-[#00b9b9]'
            }),
            'working_days': forms.NumberInput(attrs={
                'class': 'px-3 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-[#00b9b9]'
            }),
            'leave_days': forms.NumberInput(attrs={
                'class': 'px-3 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-[#00b9b9]'
            }),
            'deduction': forms.NumberInput(attrs={
                'class': 'px-3 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-[#00b9b9]'
            }),
            'status': forms.Select(attrs={
                'class': 'px-3 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-[#00b9b9]'
            }),
              'attendance_days': forms.Select(attrs={
                'class': 'px-3 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-[#00b9b9]'
            }),
        }

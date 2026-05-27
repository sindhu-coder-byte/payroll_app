from django import forms
from .models import Employee

_INPUT = 'px-3 py-1 border rounded focus:outline-none focus:ring-2 focus:ring-[#00b9b9]'


class EmployeeForm(forms.ModelForm):
    class Meta:
        model = Employee
        fields = [
            'name', 'role', 'department', 'salary', 'bonus', 'da', 'join_date',
            'work_hours', 'working_days', 'designation', 'leave_days',
            'deduction', 'status',
        ]
        widgets = {
            'join_date':    forms.DateInput(attrs={'type': 'date', 'class': _INPUT}),
            'name':         forms.TextInput(attrs={'class': _INPUT}),
            'role':         forms.TextInput(attrs={'class': _INPUT}),
            'department':   forms.TextInput(attrs={'class': _INPUT}),
            'designation':  forms.TextInput(attrs={'class': _INPUT}),
            'salary':       forms.NumberInput(attrs={'class': _INPUT}),
            'bonus':        forms.NumberInput(attrs={'class': _INPUT}),
            'da':           forms.NumberInput(attrs={'class': _INPUT}),
            'work_hours':   forms.NumberInput(attrs={'class': _INPUT}),
            'working_days': forms.NumberInput(attrs={'class': _INPUT}),
            'leave_days':   forms.NumberInput(attrs={'class': _INPUT}),
            'deduction':    forms.NumberInput(attrs={'class': _INPUT}),
            'status':       forms.Select(attrs={'class': _INPUT}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if not name:
            raise forms.ValidationError("Name is required.")
        return name

    def clean_salary(self):
        salary = self.cleaned_data.get('salary')
        if salary is not None and salary <= 0:
            raise forms.ValidationError("Salary must be greater than zero.")
        return salary

    def clean_bonus(self):
        bonus = self.cleaned_data.get('bonus')
        if bonus is not None and bonus < 0:
            raise forms.ValidationError("Bonus cannot be negative.")
        return bonus

    def clean_da(self):
        da = self.cleaned_data.get('da')
        if da is not None and da < 0:
            raise forms.ValidationError("Dearness allowance cannot be negative.")
        return da

    def clean_deduction(self):
        deduction = self.cleaned_data.get('deduction')
        if deduction is not None and deduction < 0:
            raise forms.ValidationError("Deduction cannot be negative.")
        return deduction

    def clean_work_hours(self):
        work_hours = self.cleaned_data.get('work_hours')
        if work_hours is not None and work_hours <= 0:
            raise forms.ValidationError("Work hours must be greater than zero.")
        return work_hours

    def clean_working_days(self):
        working_days = self.cleaned_data.get('working_days')
        if working_days is not None and working_days < 0:
            raise forms.ValidationError("Working days cannot be negative.")
        return working_days

    def clean_leave_days(self):
        leave_days = self.cleaned_data.get('leave_days')
        if leave_days is not None and leave_days < 0:
            raise forms.ValidationError("Leave days cannot be negative.")
        return leave_days

    def clean(self):
        cleaned_data = super().clean()
        working_days = cleaned_data.get('working_days')
        leave_days = cleaned_data.get('leave_days')
        if working_days is not None and leave_days is not None:
            if leave_days > working_days:
                raise forms.ValidationError("Leave days cannot exceed working days.")
        return cleaned_data

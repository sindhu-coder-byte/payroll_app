from django.db import models

class Employee(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=50)
    department = models.CharField(max_length=50)
    salary = models.DecimalField(max_digits=10, decimal_places=2)
    bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    designation = models.CharField(max_length=100, null=True, blank=True, default='Staff')
    join_date = models.DateField()
    work_hours = models.IntegerField()

    # Payroll-specific fields
    working_days = models.IntegerField(default=0)  
    leave_days = models.IntegerField(default=0)    
    deduction = models.DecimalField(max_digits=10, decimal_places=2, default=0)  

    # New fields
    da = models.DecimalField(max_digits=10, decimal_places=2, default=0)   # Dearness Allowance
    attendance_days = models.IntegerField(default=0)

    # Premium access flag
    is_premium = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=[
        ('Active', 'Active'),
        ('Inactive', 'Inactive'),
        ('On Leave', 'On Leave'),
    ], default='Active')

    @property
    def net_salary(self):
        """
        Calculate net salary:
        Base salary proportion to days worked + Bonus + DA - Deduction
        """
        if self.working_days > 0:
            daily_rate = self.salary / self.working_days
            earned_salary = daily_rate * (self.working_days - self.leave_days)
        else:
            earned_salary = self.salary  

        total_salary = earned_salary + self.bonus + self.da - self.deduction
        return round(total_salary, 2)

    def __str__(self):
        return self.name


class Meeting(models.Model):
    meeting_time = models.DateTimeField()
    meeting_info = models.TextField()

    def __str__(self):
        return f"{self.meeting_time} - {self.meeting_info[:20]}"
    
from django.db import migrations, models

class Migration(migrations.Migration):

    dependencies = [
        ('payroll_app', '0002_employee_is_premium_delete_customuser'),
    ]

    operations = [
        migrations.CreateModel(
            name='Meeting',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('meeting_time', models.DateTimeField()),
                ('meeting_info', models.TextField()),
            ],
        ),
    ]

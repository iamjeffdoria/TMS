from django.db import models
from django.utils.timezone import now


quarter_choices = [
    ('First Quarter', 'First Quarter'),
    ('Second Quarter', 'Second Quarter'),
    ('Third Quarter', 'Third Quarter'),
    ('Fourth Quarter', 'Fourth Quarter'),
]

class SuperAdmin(models.Model):
    username = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

    class Meta:
        verbose_name = "Super Admin"
        verbose_name_plural = "Super Admins"

class Admin(models.Model):
    username = models.CharField(max_length=255, unique=True)
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
    created_by = models.ForeignKey(SuperAdmin, on_delete=models.SET_NULL, null=True, blank=True, related_name='admins')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.full_name




class MayorsPermit(models.Model):
    control_no = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500)
    motorized_operation = models.CharField(max_length=255)
    business_name = models.CharField(max_length=255)
    expiry_date = models.DateField()
    amount_paid = models.IntegerField()
    or_no = models.CharField(max_length=100)
    issue_date = models.DateField(default=now)
    issued_at = models.CharField(max_length=255)
    mayor = models.CharField(max_length=255)
    quarter = models.CharField(
        max_length= 100,
        choices=quarter_choices,
        default='First Quarter'
    )
    status = models.CharField(
    max_length=8,
    choices=[
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('expired', 'Expired'),
    ],
    default='active'
    )

    def __str__(self):
        return f"{self.control_no} - {self.name}"
    

class IDCard(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]

    name = models.CharField(max_length=255)
    address = models.TextField()
    id_number = models.CharField(max_length=50, unique=True)
    date_of_birth = models.DateField()
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    or_number = models.CharField(max_length=50, blank=True, null=True)
    height = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # e.g., 175.50 cm
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True)  # e.g., 70.50 kg
    date_issued = models.DateField()
    expiration_date = models.DateField()
    image = models.ImageField(upload_to='idcard_images/')

    def __str__(self):
        return f"{self.name} ({self.id_number})"


    
class Mtop(models.Model):
    name = models.CharField(max_length=255)
    case_no = models.CharField(max_length=100, unique=True)
    address = models.CharField(max_length=255)
    no_of_units = models.PositiveIntegerField()
    route_operation = models.CharField(max_length=255)
    make = models.CharField(max_length=100)
    motor_no = models.CharField(max_length=100, unique=True)
    chasses_no = models.CharField(max_length=100, unique=True)
    plate_no = models.CharField(max_length=50, unique=True)
    date = models.DateField()
    municipal_treasurer = models.CharField(max_length=255)
    officer_in_charge = models.CharField(max_length=255)
    mayor = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.case_no}"
    


class Franchise(models.Model):
    name = models.CharField(max_length=255)
    denomination = models.CharField(max_length=100, blank=True, null=True)
    plate_no = models.CharField(max_length=50)
    valid_until = models.DateField()
    motor_no = models.CharField(max_length=100)
    authorized_no = models.CharField(max_length=50)
    chassis_no = models.CharField(max_length=100)
    authorized_route = models.TextField()
    purpose = models.TextField(blank=True, null=True)
    official_receipt_no = models.CharField(max_length=100)
    date = models.DateField()
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2)
    municipal_treasurer = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.name} - {self.plate_no}"



class MayorsPermitTricycle(models.Model):
    control_no = models.CharField(max_length=100, unique=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=500)
    motorized_operation = models.CharField(max_length=255)
    business_name = models.CharField(max_length=255)
    expiry_date = models.DateField()
    amount_paid = models.IntegerField()
    or_no = models.CharField(max_length=100)
    issue_date = models.DateField(default=now)
    issued_at = models.CharField(max_length=255)
    mayor = models.CharField(max_length=255)
    quarter = models.CharField(
        max_length=100,
        choices=quarter_choices,
        default='First Quarter'
    )

    status = models.CharField(
        max_length=8,
        choices=[
            ('active', 'Active'),
            ('inactive', 'Inactive'),
            ('expired', 'Expired'),
        ],
        default='active'
    )

    def __str__(self):
        return f"{self.control_no} - {self.name}"

    class Meta:
        verbose_name = "Mayor's Permit - Tricycle"
        verbose_name_plural = "Mayor's Permits - Tricycles"









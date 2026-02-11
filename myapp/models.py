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
    is_active = models.BooleanField(default=True)  # ADD THIS if missing
    created_by = models.ForeignKey(SuperAdmin, on_delete=models.SET_NULL, null=True, blank=True, related_name='admins')
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return self.full_name


class AdminPermission(models.Model):
    admin = models.OneToOneField(
        Admin,
        on_delete=models.CASCADE,
        related_name="permissions"
    )

    # Permissions
    can_access_potpot_registration = models.BooleanField(default=False)
    can_access_motorcycle_registration = models.BooleanField(default=False)

    # Who last edited this permission
    updated_by = models.ForeignKey(
        SuperAdmin,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="updated_admin_permissions"
    )

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Permissions for {self.admin.full_name}"

    class Meta:
        verbose_name = "Admin Permission"
        verbose_name_plural = "Admin Permissions"


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
    image = models.ImageField(upload_to='idcard_images/', blank=True, null=True)

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


class Tricycle(models.Model):
    STATUS_CHOICES = [
        ('New', 'New'),
        ('Renewed', 'Renewed'),
        ('Expired', 'Expired'),
        ('Inactive', 'Inactive'),
    ]
    
    body_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=200)
    address = models.TextField()
    make_kind = models.CharField(max_length=100)
    engine_motor_no = models.CharField(max_length=100)
    chassis_no = models.CharField(max_length=100)
    plate_no = models.CharField(max_length=20, unique=True)
    date_registered = models.DateField()
    date_expired = models.DateField()   
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    remarks = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return f"{self.body_number} - {self.name}"
    

class TricycleHistory(models.Model):
    """Track all historical changes and events for Tricycle records"""
    
    ACTION_CHOICES = [
        ('created', 'Created'),
        ('renewed', 'Renewed'),
        ('expired', 'Expired'),
        ('updated', 'Updated'),
        ('status_changed', 'Status Changed'),
    ]
    
    tricycle = models.ForeignKey(
        Tricycle, 
        on_delete=models.CASCADE, 
        related_name='history'
    )
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    previous_status = models.CharField(max_length=20, blank=True, null=True)
    new_status = models.CharField(max_length=20, blank=True, null=True)
    previous_date_expired = models.DateField(blank=True, null=True)
    new_date_expired = models.DateField(blank=True, null=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.CharField(max_length=100, blank=True, null=True)  # Optional: track user
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Tricycle History'
        verbose_name_plural = 'Tricycle Histories'
    
    def __str__(self):
        return f"{self.tricycle.body_number} - {self.action} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class MayorsPermitHistory(models.Model):
    permit = models.ForeignKey(
        MayorsPermit,
        on_delete=models.CASCADE,
        related_name="histories"
    )
    previous_status = models.CharField(max_length=8)
    new_status = models.CharField(max_length=8)
    activated_at = models.DateTimeField(default=now)
    remarks = models.TextField(blank=True, null=True)
    
    # Track who made the change
    updated_by_type = models.CharField(max_length=20, null=True, blank=True)  # 'admin' or 'superadmin'
    updated_by_id = models.IntegerField(null=True, blank=True)
    updated_by_name = models.CharField(max_length=255, null=True, blank=True)  # Store name for display
    
    # Alternative: Using GenericForeignKey (more flexible but complex)
    # updated_by_content_type = models.ForeignKey(ContentType, on_delete=models.SET_NULL, null=True, blank=True)
    # updated_by_object_id = models.PositiveIntegerField(null=True, blank=True)
    # updated_by = GenericForeignKey('updated_by_content_type', 'updated_by_object_id')

    def __str__(self):
        return f"{self.permit.control_no}: {self.previous_status} → {self.new_status}"
    
    class Meta:
        ordering = ['-activated_at']
        verbose_name = "Mayor's Permit History"
        verbose_name_plural = "Mayor's Permit Histories"



class MayorsPermitTricycleHistory(models.Model):
    permit = models.ForeignKey(
        MayorsPermitTricycle,
        on_delete=models.CASCADE,
        related_name="histories"
    )
    previous_status = models.CharField(max_length=8)
    new_status = models.CharField(max_length=8)
    activated_at = models.DateTimeField(default=now)
    remarks = models.TextField(blank=True, null=True)
    
    # ✅ Track who made the change
    updated_by_type = models.CharField(max_length=20, null=True, blank=True)  # 'admin' or 'superadmin'
    updated_by_id = models.IntegerField(null=True, blank=True)
    updated_by_name = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"{self.permit.control_no}: {self.previous_status} → {self.new_status}"
    
    class Meta:
        ordering = ['-activated_at']
        verbose_name = "Tricycle Permit History"
        verbose_name_plural = "Tricycle Permit Histories"




class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('create', 'Created'),
        ('update', 'Updated'),
        ('delete', 'Deleted'),
        ('status_change', 'Status Changed'),
    ]
    
    MODEL_CHOICES = [
        ('potpot', 'Potpot Permit'),
        ('motorcycle', 'Motorcycle Permit'),
        ('admin', 'Admin'),
        ('idcard', 'ID Card'),
        ('mtop', 'MTOP'),
        ('franchise', 'Franchise'),
    ]
    
    # What happened
    action = models.CharField(max_length=20, choices=ACTION_CHOICES)
    model_type = models.CharField(max_length=20, choices=MODEL_CHOICES)
    
    # Details of the change
    object_id = models.CharField(max_length=100)  # The ID or control_no of the changed object
    object_name = models.CharField(max_length=255)  # Name of the person/entity
    
    # What changed
    field_name = models.CharField(max_length=100, blank=True, null=True)  # e.g., 'address', 'amount_paid'
    old_value = models.TextField(blank=True, null=True)
    new_value = models.TextField(blank=True, null=True)
    
    # Additional context
    description = models.TextField()  # Human-readable description
    
    # Who made the change
    user_type = models.CharField(max_length=20, blank=True, null=True)  # 'admin' or 'superadmin'
    user_id = models.IntegerField(blank=True, null=True)
    user_name = models.CharField(max_length=255, blank=True, null=True)
    
    # When it happened
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-timestamp']
        verbose_name = 'Activity Log'
        verbose_name_plural = 'Activity Logs'
    
    def __str__(self):
        return f"{self.model_type} - {self.action} - {self.object_name}"



class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    is_completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title
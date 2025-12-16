from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

# ---------------- Tenant ----------------
class Tenant(models.Model):
    name = models.CharField(max_length=100, unique=True)
    domain = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name

# ---------------- Roles ----------------
class Role(models.Model):
    ROLE_CHOICES = [
        ('director', 'Director'),
        ('visitor', 'Visitor'),
        ('member', 'Member'),
        ('trainer', 'Trainer'),
        ('worker', 'Worker'),
        ('maintenance', 'Maintenance'),
    ]
    name = models.CharField(max_length=50, choices=ROLE_CHOICES, unique=True)

    def __str__(self):
        return self.name

# ---------------- User ----------------
class User(AbstractUser):
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, null=True, blank=True)
    gender = models.CharField(max_length=10, null=True, blank=True)
    qualification = models.TextField(null=True, blank=True)

    register_for_membership = models.BooleanField(default=False)
    register_for_job = models.BooleanField(default=False)
    application_status = models.CharField(max_length=50, null=True, blank=True)

    role = models.ForeignKey(Role, on_delete=models.SET_NULL, null=True, blank=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True)

    REQUIRED_FIELDS = ["email"]

    def __str__(self):
        return self.username

# ---------------- Membership ----------------
class Member(models.Model):
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    joined_at = models.DateField(auto_now_add=True)
    dob = models.DateField(null=True, blank=True)  # optional
    address = models.TextField(null=True, blank=True)  # optional

    def __str__(self):
        return self.user.username



class MembershipType(models.Model):
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_days = models.IntegerField(default=30)
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} ({self.tenant.name})"

class Membership(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    membership_type = models.ForeignKey(MembershipType, on_delete=models.CASCADE)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField()
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        username = self.user.username if self.user else "No User"
        membership_name = self.membership_type.name if self.membership_type else "No Membership"
        return f"{username} - {membership_name}"

# ---------------- Trainer / Worker / Maintenance / Director ----------------
class Trainer(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    experience_years = models.IntegerField(default=0)
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.user.username

class Worker(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.user.username

class Maintenance(models.Model):
    user = models.OneToOneField(User, on_delete=models.SET_NULL, null=True, blank=True)
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True)
    def __str__(self):
        return self.user.username

class Director(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def __str__(self):
        return self.user.username

# ---------------- Payment ----------------
class Payment(models.Model):
    STATUS_CHOICES = [
        ("created", "Created"),
        ("paid", "Paid"),
        ("failed", "Failed"),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    membership_type = models.ForeignKey(MembershipType, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=255, blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="created")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.membership_type.name} - {self.status}"

# ---------------- Interview ----------------
class InterviewStatus(models.Model):
    name = models.CharField(max_length=50)  # Pending / Passed / Failed
    def __str__(self):
        return self.name

class Interview(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    interviewer_user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="interviews_taken")
    interview_date = models.DateTimeField()
    status = models.ForeignKey(InterviewStatus, on_delete=models.SET_NULL, null=True)
    remarks = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.status.name if self.status else 'Pending'}"

# ---------------- Trainer Shift ----------------
class TrainerShift(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    day_of_week = models.CharField(max_length=20)
    shift_start_time = models.TimeField()
    shift_end_time = models.TimeField()
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.trainer.user.username} - {self.day_of_week}"

# ---------------- Classes ----------------
class Class(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    start_time = models.TimeField()
    end_time = models.TimeField()
    max_members = models.IntegerField()
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.name

# ---------------- Personal Training ----------------
class PTAssignment(models.Model):
    trainer = models.ForeignKey(Trainer, on_delete=models.CASCADE)
    member = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    fee = models.DecimalField(max_digits=10, decimal_places=2)
    sessions = models.IntegerField()
    tenant = models.ForeignKey(Tenant, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.member.username} - {self.trainer.user.username}"

from django.contrib import admin
from .models import *

# ---------------- Tenant ----------------
@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('name', 'domain')
    search_fields = ('name', 'domain')

# ---------------- Role ----------------
@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ('name',)
    list_filter = ('name',)
    search_fields = ('name',)

# ---------------- User ----------------
@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'role', 'tenant', 'is_active', 'is_staff')
    list_filter = ('role', 'tenant', 'is_active', 'is_staff')
    search_fields = ('username', 'email', 'phone')
    ordering = ('username',)

# ---------------- Membership ----------------
@admin.register(MembershipType)
class MembershipTypeAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'duration_days', 'tenant')
    list_filter = ('tenant',)
    search_fields = ('name',)

@admin.register(Membership)
class MembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'membership_type', 'start_date', 'end_date', 'tenant')
    list_filter = ('tenant', 'membership_type')
    search_fields = ('user__username',)

# ---------------- Trainer / Worker / Maintenance / Director ----------------
@admin.register(Trainer)
class TrainerAdmin(admin.ModelAdmin):
    list_display = ('user', 'experience_years', 'tenant')
    list_filter = ('tenant',)
    search_fields = ('user__username',)

@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ('user', 'tenant')
    list_filter = ('tenant',)
    search_fields = ('user__username',)

@admin.register(Maintenance)
class MaintenanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'tenant')
    list_filter = ('tenant',)
    search_fields = ('user__username',)

@admin.register(Director)
class DirectorAdmin(admin.ModelAdmin):
    list_display = ('user',)
    search_fields = ('user__username',)

# ---------------- Payment ----------------
@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('user', 'membership_type', 'amount', 'status', 'created_at')
    list_filter = ('status', 'membership_type', 'user__tenant')
    search_fields = ('user__username', 'membership_type__name', 'razorpay_order_id')

# ---------------- Interview ----------------
@admin.register(InterviewStatus)
class InterviewStatusAdmin(admin.ModelAdmin):
    list_display = ('name',)

@admin.register(Interview)
class InterviewAdmin(admin.ModelAdmin):
    list_display = ('user', 'interviewer_user', 'interview_date', 'status', 'created_at')
    list_filter = ('status', 'interview_date', 'user__tenant')
    search_fields = ('user__username', 'interviewer_user__username')

# ---------------- Trainer Shift ----------------
@admin.register(TrainerShift)
class TrainerShiftAdmin(admin.ModelAdmin):
    list_display = ('trainer', 'day_of_week', 'shift_start_time', 'shift_end_time', 'tenant')
    list_filter = ('day_of_week', 'tenant')
    search_fields = ('trainer__user__username',)

# ---------------- Classes ----------------
@admin.register(Class)
class ClassAdmin(admin.ModelAdmin):
    list_display = ('name', 'trainer', 'start_time', 'end_time', 'max_members', 'tenant')
    list_filter = ('trainer', 'tenant')
    search_fields = ('name', 'trainer__user__username')

# ---------------- Personal Training ----------------
@admin.register(PTAssignment)
class PTAssignmentAdmin(admin.ModelAdmin):
    list_display = ('member', 'trainer', 'start_date', 'end_date', 'fee', 'sessions', 'tenant')
    list_filter = ('trainer', 'tenant')
    search_fields = ('member__username', 'trainer__user__username')


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ('user', 'joined_at','dob', 'tenant')
    list_filter = ('tenant',)
    search_fields = ('user__username',)
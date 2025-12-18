from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from django.contrib.auth import authenticate
from .models import *

# ---------------- Register ----------------
class RegisterSerializer(serializers.ModelSerializer):
    tenant = serializers.PrimaryKeyRelatedField(
        queryset=Tenant.objects.all(), required=False, allow_null=True
    )
    
    class Meta:
        model = User
        fields = ["username", "email", "password", "phone", "gender", "qualification", "tenant"]
        extra_kwargs = {
            "password": {"write_only": True},
            "phone": {"required": False},
            "gender": {"required": False},
            "qualification": {"required": False}
        }

    def create(self, validated_data):
        visitor_role = Role.objects.get(name="visitor")
        user = User.objects.create(
            username=validated_data["username"],
            email=validated_data["email"],
            password=make_password(validated_data["password"]),
            phone=validated_data.get("phone", ""),
            gender=validated_data.get("gender", ""),
            qualification=validated_data.get("qualification", ""),
            role=visitor_role,
            application_status="none",
            tenant=validated_data.get("tenant", None)
        )
        return user

# ---------------- Login ----------------
class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        user = authenticate(username=data.get("username"), password=data.get("password"))
        if not user:
            raise serializers.ValidationError("Invalid username or password")
        return {"user": user}

# ---------------- Membership Purchase ----------------
class MembershipPurchaseSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    membership_type_id = serializers.IntegerField()
    shift_id = serializers.IntegerField(required=False, allow_null=True)
    class_id = serializers.IntegerField(required=False, allow_null=True)
    pt_assignment_id = serializers.IntegerField(required=False, allow_null=True)

    def validate(self, data):
        # Validate User
        try:
            user = User.objects.get(id=data["user_id"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"user_id": "User does not exist"})
        # Validate Membership Type
        try:
            membership_type = MembershipType.objects.get(id=data["membership_type_id"])
        except MembershipType.DoesNotExist:
            raise serializers.ValidationError({"membership_type_id": "MembershipType does not exist"})
        # Validate Shift if provided
        shift_id = data.get("shift_id")
        if shift_id:
            if not Shift.objects.filter(id=shift_id).exists():
                raise serializers.ValidationError({"shift_id": "Shift does not exist"})
        # Validate Class if provided
        class_id = data.get("class_id")
        if class_id:
            if not Class.objects.filter(id=class_id).exists():
                raise serializers.ValidationError({"class_id": "Class does not exist"})
        # Validate PT Assignment if provided
        pt_id = data.get("pt_assignment_id")
        if pt_id:
            if not PTAssignment.objects.filter(id=pt_id).exists():
                raise serializers.ValidationError({"pt_assignment_id": "PT Assignment does not exist"})
        return data

# ---------------- Job Apply ----------------
class JobApplySerializer(serializers.Serializer):
    experience_years = serializers.IntegerField(required=False)

# ---------------- Admin Approve Job ----------------
class ApproveJobSerializer(serializers.Serializer):
    user_id = serializers.IntegerField()
    new_role = serializers.ChoiceField(choices=["trainer", "worker", "maintenance","receptionist"])

# ---------------- Interview ----------------
class InterviewSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    interviewer_user_id = serializers.IntegerField(required=False)
    status_id = serializers.IntegerField(required=False)
    remarks = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Interview
        fields = ["user_id", "interviewer_user_id", "interview_date", "remarks", "status_id"]

    def validate(self, data):
        # ---------------- Candidate ----------------
        try:
            candidate = User.objects.get(id=data["user_id"])
        except User.DoesNotExist:
            raise serializers.ValidationError({"user_id": "User not found"})
        data["user"] = candidate

        # ---------------- Interviewer ----------------
        interviewer = self.context["request"].user
        if candidate.tenant != interviewer.tenant:
            raise serializers.ValidationError(
                "Candidate and interviewer must belong to the same tenant"
            )
        data["interviewer_user"] = interviewer

        # ---------------- STATUS (FIX) ----------------
        status_id = data.get("status_id")
        if status_id:
            try:
                status_obj = InterviewStatus.objects.get(id=status_id)
            except InterviewStatus.DoesNotExist:
                raise serializers.ValidationError({"status_id": "Invalid status id"})
        else:
            status_obj, _ = InterviewStatus.objects.get_or_create(name="Pending")

        data["status"] = status_obj
        return data

    def create(self, validated_data):
        validated_data.pop("status_id", None)
        return Interview.objects.create(
            user=validated_data["user"],
            interviewer_user=validated_data["interviewer_user"],
            interview_date=validated_data["interview_date"],
            status=validated_data["status"],
            remarks=validated_data.get("remarks", "")
        )


# ---------------- Shift ----------------
class ShiftSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    role = serializers.CharField(source='user.role.name', read_only=True)

    class Meta:
        model = Shift
        fields = ["id", "user", "username", "role", "day_of_week", "start_time", "end_time", "tenant"]


# ---------------- Class ----------------
class ClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Class
        fields = ["id", "trainer", "name", "start_time", "end_time", "max_members", "tenant"]

# ---------------- Personal Training ----------------
class PTAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = PTAssignment
        fields = ["id", "trainer", "member", "start_date", "end_date", "fee", "sessions", "tenant"]

# ---------------- Payment ----------------
class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ["id", "user", "membership_type", "amount", "razorpay_order_id", "razorpay_payment_id",
                  "razorpay_signature", "status", "created_at"]



class ReceptionistSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField(write_only=True)
    username = serializers.CharField(source="user.username", read_only=True)
    email = serializers.EmailField(source="user.email", read_only=True)
    tenant_name = serializers.CharField(source="tenant.name", read_only=True)

    class Meta:
        model = Receptionist
        fields = [
            "id",
            "user_id",
            "username",
            "email",
            "tenant",
            "tenant_name",
        ]

    def create(self, validated_data):
        user_id = validated_data.pop("user_id")
        user = User.objects.get(id=user_id)

        return Receptionist.objects.create(
            user=user,
            tenant=user.tenant
        )
        
        
        
        
        
class AttendanceSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()
    status_id = serializers.IntegerField()
    class_id = serializers.IntegerField(required=False)


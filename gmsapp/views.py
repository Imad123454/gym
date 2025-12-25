# ---------------- Django / DRF ----------------
from django.conf import settings
from django.utils import timezone
from rest_framework.parsers import MultiPartParser, FormParser
from django.views.decorators.csrf import csrf_exempt

from rest_framework.decorators import api_view, permission_classes,authentication_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status

from rest_framework_simplejwt.tokens import RefreshToken

# ---------------- Razorpay ----------------
import razorpay

# ---------------- Models ----------------
from .models import (
    User, Tenant, Role, Trainer, Worker, Maintenance, Receptionist,
    MembershipType, Payment, Membership, Member, Shift, Class,
    PTAssignment, Attendance, Inquiry
)

# ---------------- Serializers ----------------
from .serializers import (
    RegisterSerializer, LoginSerializer, MyProfileSerializer,
    JobApplySerializer, InterviewSerializer, ApproveJobSerializer,
    ShiftSerializer, ClassSerializer, PTAssignmentSerializer,
    AttendanceSerializer, InquirySerializer
)

# ---------------- Permissions ----------------
from .permissions import IsAdminOrReadOnly


client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))

# ---------------- Helper ----------------
def check_tenant(user, tenant):
    return user.tenant == tenant

# ---------------- Register ----------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def register(request):
    tenant = request.user.tenant
    if request.user.role.name != "receptionist":
        return Response({"detail": "Only receptionist can create users"}, status=403)

    serializer = RegisterSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)
    user = serializer.save(tenant=tenant)

    return Response({
        "message": "User registered successfully",
        "created_by": request.user.username,
        "tenant": tenant.name,
        "role": user.role.name,
        "username": user.username
    })

# ---------------- Login ----------------

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
@authentication_classes([])
def login(request):
    serializer = LoginSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = serializer.validated_data["user"]

    # ✅ Tenant automatically detect
    tenant_name = getattr(request, "tenant_name", user.tenant.name)

    refresh = RefreshToken.for_user(user)
    access = refresh.access_token
    access["role"] = user.role.name if user.role else None
    access["tenant"] = tenant_name

    return Response({
        "message": "Login successful",
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role.name if user.role else None,
            "tenant": tenant_name
        },
        "tokens": {
            "refresh": str(refresh),
            "access": str(access)
        }
    })

# ---------------- Logout ----------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def logout(request):
    try:
        refresh_token = request.data["refresh"]
        token = RefreshToken(refresh_token)
        token.blacklist()
        return Response({"message": "Logout successful"})
    except:
        return Response({"error": "Invalid refresh token"}, status=400)

# ---------------- Job Apply ----------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def apply_job(request):
    serializer = JobApplySerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = request.user
    user.application_status = "pending"
    user.register_for_job = True
    user.save()

    return Response({
        "message": "Job application submitted",
        "experience_years": serializer.validated_data.get("experience_years")
    })

# ---------------- Profile ----------------
@api_view(["GET", "PUT", "PATCH"])
@permission_classes([IsAuthenticated])
def my_profile(request):
    user = request.user

    # Tenant isolation check
    current_domain = request.get_host().split(":")[0]
    if user.tenant.domain != current_domain:
        return Response({"detail": "Invalid tenant"}, status=403)

    if request.method == "GET":
        serializer = MyProfileSerializer(user, context={"request": request})
        return Response(serializer.data)

    # For PUT/PATCH
    request.parsers = [MultiPartParser(), FormParser()]

    serializer = MyProfileSerializer(
        user,
        data=request.data,
        partial=True,
        context={"request": request}
    )
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response(serializer.data)
# ---------------- Interview ----------------
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminOrReadOnly])
def create_interview(request):
    serializer = InterviewSerializer(data=request.data, context={"request": request})
    if serializer.is_valid():
        interview = serializer.save()
        return Response({
            "message": "Interview created successfully",                      
            "interview": {
                "id": interview.id,
                "user": interview.user.username,
                "interviewer": interview.interviewer_user.username,
                "interview_date": interview.interview_date,
                "status": interview.status.name,
                "remarks": interview.remarks
            }
        }, status=201)
    return Response(serializer.errors, status=400)

# ---------------- Approve Job ----------------
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminOrReadOnly])
def approve_job(request):
    serializer = ApproveJobSerializer(data=request.data)
    serializer.is_valid(raise_exception=True)

    user = User.objects.get(id=serializer.validated_data["user_id"])
    new_role_name = serializer.validated_data["new_role"]

    new_role = Role.objects.get(name=new_role_name)
    user.role = new_role
    user.application_status = "approved"
    user.save()

    # Profile creation
    if new_role_name == "trainer":
        Trainer.objects.get_or_create(user=user, tenant=user.tenant)
    elif new_role_name == "worker":
        Worker.objects.get_or_create(user=user, tenant=user.tenant)
    elif new_role_name == "maintenance":
        Maintenance.objects.get_or_create(user=user, tenant=user.tenant)
    elif new_role_name == "receptionist":
        Receptionist.objects.get_or_create(user=user, tenant=user.tenant)

    return Response({"message": f"User role updated → {new_role.name} and profile created"})

# ---------------- Create Payment Order ----------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_payment_order(request):
    user = request.user
    membership_type_id = request.data.get("membership_type_id")
    try:
        membership_type = MembershipType.objects.get(id=membership_type_id, tenant=user.tenant)
    except MembershipType.DoesNotExist:
        return Response({"error": "Invalid membership type"}, status=404)

    amount_in_paise = int(membership_type.price * 100)
    razorpay_order = client.order.create({
        "amount": amount_in_paise,
        "currency": "INR",
        "payment_capture": "1"
    })

    payment = Payment.objects.create(
        user=user,
        membership_type=membership_type,
        amount=membership_type.price,
        razorpay_order_id=razorpay_order["id"],
        status="created"
    )

    return Response({
        "message": "Razorpay order created",
        "order_id": razorpay_order["id"],
        "amount": membership_type.price,
        "currency": "INR"
    })

# ---------------- Verify Payment ----------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def verify_payment(request):
    user = request.user
    order_id = request.data.get("order_id")
    shift_id = request.data.get("shift_id")
    class_id = request.data.get("class_id")
    
    try:
        payment = Payment.objects.get(user=user, razorpay_order_id=order_id)
    except Payment.DoesNotExist:
        return Response({"error": "Payment record not found"}, status=404)

    payment.status = "paid"
    payment.save()

    # ---------------- Membership ----------------
    start_date = timezone.now().date()
    end_date = start_date + timezone.timedelta(days=payment.membership_type.duration_days)
    membership = Membership.objects.create(
        user=user,
        membership_type=payment.membership_type,
        start_date=start_date,
        end_date=end_date,
        tenant=user.tenant
    )

    # ---------------- User role update ----------------
    member_role = Role.objects.get(name="member")
    user.role = member_role
    user.register_for_membership = True
    user.save()

    # ---------------- Member object ----------------
    member = Member.objects.create(
        tenant=user.tenant,
        user=user,
        joined_at=start_date
    )

    response_data = {
        "membership": {
            "user": user.username,
            "membership_type": payment.membership_type.name,
            "start_date": str(start_date),
            "end_date": str(end_date),
            "tenant": user.tenant.name
        },
        "member": {
            "user": user.username,
            "tenant": user.tenant.name,
            "joined_at": str(member.joined_at)
        }
    }

    # Optional: assign shift/class if ids provided
    if shift_id:
        shift = Shift.objects.get(id=shift_id, tenant=user.tenant)
        response_data["shift"] = {
            "user": shift.user.username,
            "day_of_week": shift.day_of_week,
            "start_time": str(shift.start_time),
            "end_time": str(shift.end_time)
        }

    if class_id:
        try:
            cls = Class.objects.get(id=class_id)
            response_data["class"] = {
                "name": cls.name,
                "trainer": cls.trainer.user.username,
                "start_time": str(cls.start_time),
                "end_time": str(cls.end_time)
            }
        except Class.DoesNotExist:
            response_data["class"] = None

    return Response({
        "message": "Payment verified, membership purchased & member created successfully!",
        "data": response_data
    })

# ---------------- Shift ----------------
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated, IsAdminOrReadOnly])
def shift_view(request):
    if request.method == "POST":
        user_id = request.data.get("user_id")
        day_of_week = request.data.get("day_of_week")
        start_time = request.data.get("start_time")
        end_time = request.data.get("end_time")

        try:
            user_obj = User.objects.get(id=user_id, tenant=request.user.tenant)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=404)

        shift = Shift.objects.create(
            user=user_obj,
            day_of_week=day_of_week,
            start_time=start_time,
            end_time=end_time,
            tenant=request.user.tenant
        )

        return Response({"message": f"Shift created for {user_obj.username}"})

    shifts = Shift.objects.filter(tenant=request.user.tenant)
    serializer = ShiftSerializer(shifts, many=True)
    return Response(serializer.data)

# ---------------- Class ----------------
@api_view(["GET", "POST"])
@permission_classes([IsAuthenticated])
def class_view(request):
    user = request.user

    if user.tenant.domain != request.get_host().split(":")[0]:
        return Response({"detail": "Invalid tenant"}, status=403)

    if request.method == "POST":
        trainer_id = request.data.get("trainer_id")
        name = request.data.get("name")
        start_time = request.data.get("start_time")
        end_time = request.data.get("end_time")
        max_members = request.data.get("max_members")

        try:
            trainer = Trainer.objects.get(id=trainer_id, tenant=user.tenant)
        except Trainer.DoesNotExist:
            return Response({"error": "Trainer not found or not in your tenant"}, status=404)

        class_obj = Class.objects.create(
            trainer=trainer,
            name=name,
            start_time=start_time,
            end_time=end_time,
            max_members=max_members,
            tenant=user.tenant
        )

        return Response({"message": f"Class '{name}' created for trainer {trainer.user.username}"})

    if user.role.name == "director":
        classes = Class.objects.all()
    elif user.role.name == "trainer":
        trainer = Trainer.objects.get(user=user)
        classes = Class.objects.filter(trainer=trainer)
    else:
        classes = Class.objects.filter(tenant=user.tenant)

    serializer = ClassSerializer(classes, many=True)
    return Response(serializer.data)

# ---------------- PT Assignment ----------------
@api_view(["POST"])
@permission_classes([IsAuthenticated, IsAdminOrReadOnly])
def create_pt_assignment(request):
    trainer_id = request.data.get("trainer_id")
    member_id = request.data.get("member_id")
    start_date = request.data.get("start_date")
    end_date = request.data.get("end_date")
    fee = request.data.get("fee")
    sessions = request.data.get("sessions")

    try:
        trainer = Trainer.objects.get(id=trainer_id, tenant=request.user.tenant)
        member = User.objects.get(id=member_id, role__name="member", tenant=request.user.tenant)
    except (Trainer.DoesNotExist, User.DoesNotExist):
        return Response({"error": "Trainer or Member not found"}, status=404)

    pt = PTAssignment.objects.create(
        trainer=trainer,
        member=member,
        start_date=start_date,
        end_date=end_date,
        fee=fee,
        sessions=sessions,
        tenant=request.user.tenant
    )

    return Response({"message": f"PT Assignment created for member {member.username} with trainer {trainer.user.username}"})

# ---------------- Attendance ----------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def mark_attendance(request):
    serializer = AttendanceSerializer(
        data=request.data,
        context={"request": request}
    )
    serializer.is_valid(raise_exception=True)
    attendance = serializer.save()

    return Response({
        "message": "Attendance marked successfully",
        "user": attendance.user.username,
        "role": attendance.role,
        "date": attendance.date,
        "status": attendance.status.name
    }, status=201)

# ---------------- Inquiry ----------------
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def inquiry_create_view(request):
    serializer = InquirySerializer(data=request.data, context={"request": request})
    serializer.is_valid(raise_exception=True)
    serializer.save()
    return Response({"message": "Inquiry submitted successfully"}, status=status.HTTP_201_CREATED)

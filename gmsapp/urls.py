from django.urls import path
from . import views

urlpatterns = [
    # Auth
    path("register/", views.register),
    path("login/", views.login),
    path("logout/", views.logout),

    # Payment / Membership
    path("create-payment-order/", views.create_payment_order),
    path("verify-payment/", views.verify_payment),

    # Job Application
    path("apply-job/", views.apply_job),
    path("create-interview/", views.create_interview),
    path("approve-job/", views.approve_job),

    # Trainer workflow
    path("shifts/", views.shift_view),
    path("classes/", views.class_view),
    path("trainer/create-pt-assignment/", views.create_pt_assignment),
]

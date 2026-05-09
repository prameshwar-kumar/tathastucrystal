from django.urls import path
from . import views

app_name = "account"

urlpatterns = [

    # ========================
    # DASHBOARD / PROFILE
    # ========================
    path("dashboard/", views.dashboard, name="dashboard"),
    path("profile/", views.profile_view, name="profile"),

    # ========================
    # AUTHENTICATION
    # ========================
    path("login/", views.login_view, name="login"),
    path("register/", views.register_view, name="register"),
    path("logout/", views.logout_view, name="logout"),

    # ========================
    # EMAIL OTP
    # ========================
    path("verify-email/", views.verify_email_otp, name="verify_email"),
    path("resend-otp/", views.resend_email_otp, name="resend_otp"),

    # ========================
    # PASSWORD RESET (CUSTOM)
    # ========================
    path("forgot-password/", views.forgot_password, name="forgot_password"),
    path("reset-password/<uidb64>/<token>/", views.reset_password, name="reset_password"),

    # ========================
    # ADDRESS MANAGEMENT
    # ========================
    path("addresses/", views.address_list, name="address_list"),
    path("addresses/add/", views.address_add, name="address_add"),
    path("addresses/edit/<int:id>/", views.address_edit, name="address_edit"),
    path("addresses/delete/<int:id>/", views.address_delete, name="address_delete"),
    path("addresses/default/<int:id>/", views.address_set_default, name="address_set_default"),
]

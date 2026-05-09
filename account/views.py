from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect, get_object_or_404
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.core.mail import send_mail

from .models import CustomUser, Address
from order.models import Order

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

import random
from datetime import timedelta


# ======================================================
# OTP HELPER
# ======================================================
def generate_otp():
    return str(random.randint(100000, 999999))


# ======================================================
# LOGIN
# ======================================================
def login_view(request):
    if request.user.is_authenticated:
        return redirect("account:dashboard")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        user = authenticate(request, email=email, password=password)

        if user:
            if not user.is_email_verified:
                messages.warning(request, "Please verify your email first.")
                return redirect("account:register")

            login(request, user)


            next_url = request.GET.get("next", "account:dashboard")
            return redirect(next_url)

        messages.error(request, "Invalid email or password")

    return render(request, "account/login.html")


# ======================================================
# REGISTER + OTP SEND
# ======================================================
def register_view(request):
    if request.user.is_authenticated:
        return redirect("account:dashboard")

    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")
        username = request.POST.get("username", "")

        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already registered")
            return redirect("account:register")

        user = CustomUser.objects.create_user(
            email=email,
            password=password,
            username=username,
            is_email_verified=False,
        )

        # CREATE OTP
        otp = generate_otp()

        request.session["email_otp"] = otp
        request.session["otp_expiry"] = (
            timezone.now() + timedelta(minutes=10)
        ).isoformat()
        request.session["verify_user_id"] = user.id

        # SEND OTP (Console / SMTP)
        send_mail(
            subject="Verify your email",
            message=f"Your OTP is: {otp}",
            from_email=None,
            recipient_list=[email],
        )

        messages.success(request, "OTP sent. Check your email.")
        return redirect("account:verify_email")

    return render(request, "account/register.html")


# ======================================================
# VERIFY EMAIL OTP
# ======================================================
def verify_email_otp(request):
    user_id = request.session.get("verify_user_id")
    if not user_id:
        return redirect("account:login")

    user = get_object_or_404(CustomUser, id=user_id)

    if request.method == "POST":
        entered_otp = request.POST.get("otp")
        saved_otp = request.session.get("email_otp")
        expiry_raw = request.session.get("otp_expiry")

        expiry = parse_datetime(expiry_raw) if expiry_raw else None

        if not saved_otp or not expiry or timezone.now() > expiry:
            messages.error(request, "OTP expired. Please register again.")
            request.session.flush()
            return redirect("account:register")

        if entered_otp == saved_otp:
            user.is_email_verified = True
            user.save()

            request.session.flush()

            login(request, user)

            messages.success(request, "Email verified successfully.")
            return redirect("account:dashboard")

        messages.error(request, "Invalid OTP")

    return render(request, "account/verify_email.html")


# ======================================================
# RESEND OTP
# ======================================================
def resend_email_otp(request):
    user_id = request.session.get("verify_user_id")
    if not user_id:
        return redirect("account:login")

    otp = generate_otp()
    request.session["email_otp"] = otp
    request.session["otp_expiry"] = (
        timezone.now() + timedelta(minutes=10)
    ).isoformat()

    user = CustomUser.objects.get(id=user_id)

    send_mail(
        "Resend OTP",
        f"Your new OTP is: {otp}",
        None,
        [user.email],
    )

    messages.success(request, "OTP resent.")
    return redirect("account:verify_email")


# ======================================================
# LOGOUT
# ======================================================
@login_required
def logout_view(request):
    logout(request)
    return redirect("/")


# ======================================================
# DASHBOARD / PROFILE
# ======================================================
@login_required
def dashboard(request):
    user = request.user
    addresses = Address.objects.filter(user=user)
    orders = Order.objects.filter(user=user).order_by("-created_at")

    return render(
        request,
        "account/dashboard.html",
        {
            "user_obj": user,
            "addresses": addresses,
            "orders": orders,
        },
    )


@login_required
def profile_view(request):
    return render(request, "account/profile.html")


# ======================================================
# ADDRESS MANAGEMENT
# ======================================================
@login_required
def address_list(request):
    addresses = Address.objects.filter(user=request.user)
    return render(request, "account/address_list.html", {"addresses": addresses})


@login_required
def address_add(request):
    if request.method == "POST":
        Address.objects.create(
            user=request.user,
            full_name=request.POST.get("full_name"),
            phone=request.POST.get("phone"),
            address_line_1=request.POST.get("address_line_1"),
            address_line_2=request.POST.get("address_line_2", ""),
            city=request.POST.get("city"),
            state=request.POST.get("state"),
            pincode=request.POST.get("pincode"),
            address_type=request.POST.get("address_type"),
        )
        messages.success(request, "Address added successfully.")
        return redirect("account:address_list")

    return render(request, "account/address_form.html")


@login_required
def address_edit(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)

    if request.method == "POST":
        for field in [
            "full_name",
            "phone",
            "address_line_1",
            "address_line_2",
            "city",
            "state",
            "pincode",
            "address_type",
        ]:
            setattr(address, field, request.POST.get(field))
        address.save()

        messages.success(request, "Address updated.")
        return redirect("account:address_list")

    return render(request, "account/address_form.html", {"address": address})


@login_required
def address_delete(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)
    address.delete()
    messages.success(request, "Address deleted.")
    return redirect("account:address_list")

@login_required
def address_set_default(request, id):
    address = get_object_or_404(Address, id=id, user=request.user)

    Address.objects.filter(user=request.user).update(is_default=False)
    address.is_default = True
    address.save()

    messages.success(request, "Default address updated.")
    return redirect("account:address_list")


# ======================================================
# FORGOT PASSWORD
# ======================================================
def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")

        try:
            user = CustomUser.objects.get(email=email)
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            reset_url = request.build_absolute_uri(
                f"/account/reset-password/{uid}/{token}/"
            )

            send_mail(
                "Password Reset",
                f"Reset your password: {reset_url}",
                None,
                [email],
            )

            messages.success(request, "Password reset link sent.")
        except CustomUser.DoesNotExist:
            messages.error(request, "No user with this email.")

        return redirect("account:forgot_password")

    return render(request, "account/forgot_password.html")


def reset_password(request, uidb64, token):
    try:
        uid = urlsafe_base64_decode(uidb64).decode()
        user = CustomUser.objects.get(pk=uid)
    except Exception:
        user = None

    if user and default_token_generator.check_token(user, token):
        if request.method == "POST":
            p1 = request.POST.get("password1")
            p2 = request.POST.get("password2")

            if p1 != p2:
                messages.error(request, "Passwords do not match")
            else:
                user.set_password(p1)
                user.save()
                messages.success(request, "Password reset successful")
                return redirect("account:login")

        return render(request, "account/reset_password.html")

    messages.error(request, "Invalid or expired link")
    return redirect("account:forgot_password")

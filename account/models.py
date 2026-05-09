from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)
from django.utils import timezone


# =====================================================
# CUSTOM USER MANAGER
# =====================================================
class CustomUserManager(BaseUserManager):

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")

        email = self.normalize_email(email)
        extra_fields.setdefault("is_active", True)

        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_email_verified", True)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True")

        return self.create_user(email, password, **extra_fields)


# =====================================================
# CUSTOM USER MODEL
# =====================================================
class CustomUser(AbstractBaseUser, PermissionsMixin):

    email = models.EmailField(unique=True, db_index=True)
    username = models.CharField(
        max_length=150,
        blank=True,
        help_text="Display name (optional)"
    )
    phone = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="Optional mobile number for future OTP"
    )

    is_email_verified = models.BooleanField(default=False)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    date_joined = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    objects = CustomUserManager()

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"

    def __str__(self):
        return self.email


# =====================================================
# ADDRESS MODEL
# =====================================================
class Address(models.Model):

    ADDRESS_TYPE_CHOICES = (
        ("shipping", "Shipping"),
        ("billing", "Billing"),
    )

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name="addresses"
    )

    full_name = models.CharField(max_length=150)
    phone = models.CharField(max_length=15)

    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)

    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    pincode = models.CharField(max_length=10)

    address_type = models.CharField(
        max_length=10,
        choices=ADDRESS_TYPE_CHOICES
    )

    is_default = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        ordering = ["-is_default", "-created_at"]

    def save(self, *args, **kwargs):
        # Ensure only ONE default address per user per type
        if self.is_default:
            Address.objects.filter(
                user=self.user,
                address_type=self.address_type,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.city}"

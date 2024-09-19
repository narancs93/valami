from django.contrib.auth.models import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin
from django.contrib.auth.models import BaseUserManager
from django.db import models, transaction


def _post_create_user(user):
    """
    Create records related to the user

    Args:
        user (users.models.User): the user that was just created
    """
    Profile.objects.create(user=user)


class UserManager(BaseUserManager):
    """User manager for custom user model"""

    use_in_migrations = True

    @transaction.atomic
    def _create_user(self, username, email, password, **extra_fields):
        """Create and save a user with the given email and password"""
        email = self.normalize_email(email)
        fields = {**extra_fields, "email": email}
        if username is not None:
            fields["username"] = username
        user = self.model(**fields)
        user.set_password(password)
        user.save(using=self._db)
        _post_create_user(user)
        return user

    def create_user(self, username, email=None, password=None, **extra_fields):
        """Create a user"""
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password, **extra_fields):
        """Create a superuser"""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")  # noqa: EM101
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")  # noqa: EM101

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    EMAIL_FIELD = "email"
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ["email", "name"]

    username = models.CharField(unique=True, max_length=50)
    email = models.EmailField(blank=False, unique=True)
    name = models.CharField(blank=True, default="", max_length=255)
    is_staff = models.BooleanField(
        default=False, help_text="The user can access the admin site"
    )
    is_active = models.BooleanField(
        default=False, help_text="The user account is active"
    )

    objects = UserManager()

    def __str__(self):
        return f"User username={self.username} email={self.email}"


class Profile(models.Model):
    THEME_CHOICES = [
        ("sap_fiori_3", "SAP Fiori 3 Light"),
        ("sap_fiori_3_dark", "SAP Fiori 3 Dark"),
        ("sap_fiori_3_hcb", "SAP Fiori 3 Light (High Contrast)"),
        ("sap_fiori_3_hcw", "SAP Fiori 3 Dark (High Contrast)"),
        ("sap_horizon", "SAP Horizon Light"),
        ("sap_horizon_dark", "SAP Horizon Dark"),
        ("sap_horizon_hcb", "SAP Horizon Light (High Contrast)"),
        ("sap_horizon_hcw", "SAP Horizon Dark (High Contrast)"),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    location = models.CharField(max_length=100, blank=True, null=True)
    theme_preference = models.CharField(
        max_length=16, choices=THEME_CHOICES, default="sap_horizon"
    )

    def __str__(self):
        return f"Profile for {self.user}"

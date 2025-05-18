from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import get_user_model


def profile_pic_upload_path(instance, filename):
    """Generate upload path for profile pictures"""
    return f'profile_pics/user_{instance.id}/{filename}'

class CustomUser(AbstractUser):
    """Extended user model with profile picture and improved security"""
    email = models.EmailField(_('email address'), unique=True)  # ✅ Email must be unique
    profile_picture = models.ImageField(
        upload_to=profile_pic_upload_path,
        null=True,
        blank=True
    )

    USERNAME_FIELD = 'email'  # ✅ Using email for authentication
    REQUIRED_FIELDS = ['username']

    # Permissions
    groups = models.ManyToManyField(Group, blank=True)
    user_permissions = models.ManyToManyField(Permission, blank=True)

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def save(self, *args, **kwargs):
        """Delete old profile picture when uploading a new one"""
        if self.pk:
            try:
                old_user = CustomUser.objects.get(pk=self.pk)
                if old_user.profile_picture and old_user.profile_picture != self.profile_picture:
                    old_user.profile_picture.delete(save=False)
            except CustomUser.DoesNotExist:
                pass
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        """Delete profile picture when user is deleted"""
        if self.profile_picture:
            self.profile_picture.delete(save=False)
        super().delete(*args, **kwargs)

class Ingredient(models.Model):
    """Model representing user-specific ingredients"""
    user = models.ForeignKey(
        get_user_model(),  # ✅ Dynamically references CustomUser
        on_delete=models.CASCADE, 
        related_name="ingredients"
    )  
    name = models.CharField(
        max_length=100,
        help_text=_("Name of the ingredient")
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "name"], name="unique_user_ingredient")
        ]
        ordering = ["name"]
        verbose_name = _("Ingredient")
        verbose_name_plural = _("Ingredients")

    def __str__(self):
        return f"{self.name} (User: {self.user.username})"
    
    # class BMIRecord(models.Model):
    # user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # height = models.FloatField()
    # weight = models.FloatField()
    # bmi = models.FloatField()
    # created_at = models.DateTimeField(auto_now_add=True)

    # def __str__(self):
    #     return f"BMI {self.bmi} for {self.user.username}"
from django.conf import settings
from django.utils.translation import gettext_lazy as _



class UserWeight(models.Model):
    """Tracks user weight, BMI, and progress with validation."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # ✅ Uses dynamic user model reference
        on_delete=models.CASCADE,
        related_name="weight_records"
    )
    date = models.DateField(auto_now_add=True)  # ✅ Automatically sets entry date
    weight = models.FloatField(
        validators=[
            MinValueValidator(20, message=_("Weight must be at least 20kg")),
            MaxValueValidator(300, message=_("Weight must be less than 300kg"))
        ],
        help_text=_("User's weight in kilograms.")
    )
    bmi = models.FloatField(
        validators=[
            MinValueValidator(10, message=_("Invalid BMI value")),
            MaxValueValidator(60, message=_("Invalid BMI value"))
        ],
        help_text=_("Calculated Body Mass Index (BMI).")
    )
    notes = models.TextField(blank=True, null=True, help_text=_("Optional notes on user progress."))

    class Meta:
        ordering = ["-date"]
        verbose_name = _("Weight Record")
        verbose_name_plural = _("Weight Records")
        get_latest_by = "date"
        constraints = [
            models.UniqueConstraint(fields=["user", "date"], name="unique_weight_entry_per_day"),
        ]  # ✅ Ensures one weight entry per user per day

    def __str__(self):
        return f"{self.user.email} - {self.weight}kg on {self.date} (BMI: {self.bmi})"


class UserProfile(models.Model):
    """Additional user profile information"""
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    height = models.FloatField(
        null=True,
        blank=True,
        validators=[
            MinValueValidator(100, message="Height must be at least 100cm"),
            MaxValueValidator(250, message="Height must be less than 250cm")
        ],
        help_text="Height in centimeters"
    )
    birth_date = models.DateField(null=True, blank=True)
    dietary_preferences = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    def __str__(self):
        return f"Profile of {self.user.email}"

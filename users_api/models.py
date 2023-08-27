from django.db import models
from django.contrib.auth.models import AbstractUser, Group, Permission
from django.utils.translation import gettext as _

from django.utils import timezone

class CustomUser(AbstractUser):
    email = models.EmailField(_('email address'), unique=True)
    biography = models.TextField(blank=True, null=True)
    profile_picture = models.URLField(blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)
    password_reset_token = models.CharField(max_length=32, blank=True, null=True)

    # Set default value function for created_at
    created_at = models.DateTimeField(default=timezone.now, blank=True)

    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        permissions = [
            ("can_upload_images", "Can upload images"),
            # Add other permissions as needed
        ]

    groups = models.ManyToManyField(
        Group,
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name='custom_users_groups'
    )
    
    user_permissions = models.ManyToManyField(
        Permission,
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name='custom_users_permissions'
    )


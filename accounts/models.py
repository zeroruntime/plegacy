from django.db import models
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Adds year_group and role fields for PRESEC alumni management.
    """
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('president', 'Year Group President'),
    ]
    
    year_group = models.CharField(
        max_length=10,
        help_text="Year group (e.g., 1998, 2005, 2015, 1993_shs, 1993_olevel)",
        blank=True
    )
    
    role = models.CharField(
        max_length=20,
        choices=ROLE_CHOICES,
        default='president',
        help_text="User role in the system"
    )
    
    class Meta:
        ordering = ['-date_joined']
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        constraints = [
        models.UniqueConstraint(
            fields=['year_group', 'role'],
            condition=models.Q(role='president'),
            name='unique_president_per_year_group'
        )
    ]
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.year_group}) - {self.get_role_display()}"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_president(self):
        return self.role == 'president'

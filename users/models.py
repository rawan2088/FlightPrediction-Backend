from django.db import models

# Create your models here.
from django.contrib.auth.models import AbstractUser


# Custom user model extending AbstractUser
class User(AbstractUser):
    # Email should be unique
    email = models.EmailField(unique=True)
       
    # # User preferences for flight predictions
    # preferred_airline = models.CharField(max_length=100, blank=True)
    # preferred_airport = models.CharField(max_length=100, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # for debugging purposes
    def __str__(self):
        return self.email
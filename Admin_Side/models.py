from django.db import models

# Create your models here.
class AdminRegister(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=255)
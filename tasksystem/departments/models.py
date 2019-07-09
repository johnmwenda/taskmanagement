from django.db import models

# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length=100)

class Category(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, blank=True, null=True)
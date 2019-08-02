from django.db import models

# Create your models here.

class Department(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    email = models.EmailField(max_length=255, null=False, blank=False, unique=True)

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField(max_length=100)
    department = models.ForeignKey(Department, blank=True, null=True)

    def __str__(self):
        return f'{self.name} - {self.department}'
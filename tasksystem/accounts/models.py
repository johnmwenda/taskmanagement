from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin

from tasksystem.accounts.managers import UserManager
from tasksystem.departments.models import Department

# Create your models here.
class User(AbstractBaseUser, PermissionsMixin):
    date_joined = models.DateTimeField(auto_now_add=True)
    email = models.EmailField(max_length=255, unique=True)
    first_name = models.CharField(max_length=255)
    last_name = models.CharField(max_length=255)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_manager = models.BooleanField(default=False)
    is_member = models.BooleanField(default=False)
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)
    follows = models.ManyToManyField(
        'self',
        related_name='followed_by',
        symmetrical=False,
        blank=True,
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'

    class Meta:
        app_label = 'accounts'

    def __str__(self):
        return self.email

    def get_short_name(self):
        return self.email

    def get_full_name(self):
        return self.email

    def save(self, *args, **kwargs):
        if not self.password:
            self.password = str(uuid.uuid4()).replace('-', '')
        super(User, self).save(*args, **kwargs)

    # def delete(self, *args, **kwargs):
    #     print("called")
    #     # super().delete(*args, **kwargs)

    

    # def get_manager_object(self):
    #     if self.is_manager:
    #         return self
    #     else:
    #         pass
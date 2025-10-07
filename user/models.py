from django.db import models
from django.contrib.auth.models import User
from staff.models import StaffModel


# Create your models here.
class UserRoleModel(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    staff = models.ForeignKey(StaffModel, on_delete=models.CASCADE, null=True, blank=True)
    role = models.CharField(max_length=100)

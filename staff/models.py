from django.db import models


class StaffModel(models.Model):
    """"""
    full_name = models.CharField(max_length=50)
    image = models.FileField(upload_to='images/staff_images', blank=True, null=True)
    residential_address = models.CharField(max_length=200, blank=True, null=True)
    mobile = models.CharField(max_length=20, blank=True, null=True)
    email = models.CharField(max_length=100, null=True, blank=True)

    POSITION = (
        ('', '----------'), ('staff', 'SELLER'), ('manager', 'MANAGER'), ('admin', 'ADMIN')
    )

    position = models.CharField(max_length=100, choices=POSITION)
    salary = models.FloatField()
    bank_name = models.CharField(max_length=100, null=True, blank=True)
    account_name = models.CharField(max_length=100, null=True, blank=True)
    account_number = models.CharField(max_length=50, null=True, blank=True)
    GENDER = (
        ('male', 'MALE'), ('female', 'FEMALE')
    )

    gender = models.CharField(max_length=10, choices=GENDER, null=True, blank=True)
    registration_date = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    status = models.CharField(max_length=15, blank=True, default='active')

    def __str__(self):
        return self.full_name




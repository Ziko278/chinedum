from django.db import models
from staff.models import StaffModel


class CustomerModel(models.Model):
    """"""
    full_name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=20, null=True, blank=True)
    residential_address = models.CharField(max_length=200, null=True, blank=True)
    image = models.FileField(upload_to='images/customer_images', blank=True, null=True)
    balance = models.FloatField(blank=True, default=0)
    crate_balance = models.IntegerField(blank=True, default=0)
    amount_bought = models.FloatField(blank=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(StaffModel, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.full_name


class SaleRepModel(models.Model):
    """"""
    full_name = models.CharField(max_length=50)
    mobile = models.CharField(max_length=20, null=True, blank=True)
    residential_address = models.CharField(max_length=200, null=True, blank=True)
    image = models.FileField(upload_to='images/sale_rep_images', blank=True, null=True)
    max_credit = models.FloatField()
    credit = models.FloatField(blank=True, default=0)
    crate_credit = models.FloatField(blank=True, default=0)
    total_amount_bought = models.FloatField(blank=True, default=0)
    status = models.CharField(max_length=15, blank=True, default='active')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(StaffModel, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.full_name



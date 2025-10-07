from django.db import models
from staff.models import StaffModel
from inventory.models import InventoryModel, StockInModel
from customer.models import CustomerModel, SaleRepModel


class SaleModel(models.Model):
    """"""
    inventory = models.ForeignKey(InventoryModel, null=True, on_delete=models.SET_NULL)
    stock = models.ForeignKey(StockInModel, on_delete=models.CASCADE)
    sale_id = models.IntegerField()
    quantity = models.FloatField()
    crate_brought = models.FloatField()
    crate_remaining = models.FloatField()
    unit_selling_price = models.FloatField(null=True, blank=True)
    total_price = models.FloatField()
    date = models.DateField(auto_now_add=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(StaffModel, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.inventory.name


class SaleSummaryModel(models.Model):
    """"""
    sale_id = models.IntegerField()
    previous_balance = models.FloatField(blank=True, null=True)
    grand_total = models.FloatField()
    cash_paid = models.FloatField()
    transfer_paid = models.FloatField()
    amount_paid = models.FloatField()
    current_balance = models.FloatField()
    total_crate = models.FloatField()
    crate_owed = models.FloatField()
    client_detail = models.CharField(max_length=100, null=True, blank=True)
    customer = models.ForeignKey(CustomerModel, null=True, blank=True, on_delete=models.SET_NULL)
    sale_rep = models.ForeignKey(SaleRepModel, null=True, blank=True, on_delete=models.SET_NULL)
    client_type = models.CharField(max_length=15)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date = models.DateField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(StaffModel, on_delete=models.SET_NULL, null=True, blank=True)


class TransactionModel(models.Model):
    transaction_type = models.CharField(max_length=20)
    client_type = models.CharField(max_length=20)
    client_detail = models.CharField(max_length=100, null=True, blank=True)
    customer = models.ForeignKey(CustomerModel, null=True, blank=True, on_delete=models.SET_NULL)
    sale_rep = models.ForeignKey(SaleRepModel, null=True, blank=True, on_delete=models.SET_NULL)
    sale = models.ForeignKey(SaleSummaryModel, on_delete=models.CASCADE, null=True, blank=True)
    inventory = models.ForeignKey(InventoryModel, null=True, blank=True, on_delete=models.SET_NULL)
    cash_refund = models.FloatField(blank=True, default=0)
    crate_refund = models.FloatField(null=True, blank=True)
    total_balance = models.FloatField()
    total_crate_balance = models.FloatField()
    date = models.DateField(auto_now_add=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(StaffModel, on_delete=models.SET_NULL, null=True, blank=True)


class LodgementModel(models.Model):
    lodgement = models.FloatField()
    present_till = models.FloatField()
    date = models.DateField(auto_now_add=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(StaffModel, on_delete=models.SET_NULL, null=True, blank=True)
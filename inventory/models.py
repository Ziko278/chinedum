from django.db import models
from staff.models import StaffModel


class InventoryModel(models.Model):
    """"""
    name = models.CharField(max_length=50)
    quantity_left = models.FloatField(blank=True, default=0)
    low_level = models.IntegerField(null=True, blank=True)
    selling_price = models.FloatField()
    empty = models.FloatField()
    owed_empty = models.FloatField(blank=True, default=0)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    created_by = models.ForeignKey(StaffModel, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class StockInModel(models.Model):
    """"""
    inventory = models.ForeignKey(InventoryModel, on_delete=models.CASCADE)
    quantity_bought = models.FloatField()
    empty = models.FloatField()
    quantity_left = models.FloatField(blank=True, default=0)
    total_cost_price = models.FloatField()
    unit_cost_price = models.FloatField()
    status = models.CharField(max_length=15, blank=True, default='active')
    batch = models.IntegerField()
    date = models.DateField(auto_now_add=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(StaffModel, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.inventory.name


class StockOutModel(models.Model):
    """"""
    stock = models.ForeignKey(StockInModel, on_delete=models.CASCADE)
    inventory = models.ForeignKey(InventoryModel, on_delete=models.CASCADE)
    quantity = models.FloatField()
    worth = models.FloatField()
    empty = models.FloatField()
    remark = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(StaffModel, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.stock.inventory.name


class StockOutCrateModel(models.Model):
    """"""
    inventory = models.ForeignKey(InventoryModel, on_delete=models.CASCADE)
    quantity = models.FloatField()
    remark = models.TextField(null=True, blank=True)
    date = models.DateField(auto_now_add=True, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(StaffModel, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.inventory.name



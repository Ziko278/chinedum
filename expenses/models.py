from django.db import models
from staff.models import StaffModel


class ExpenseTypeModel(models.Model):
    """"""
    name = models.CharField(max_length=50)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    created_by = models.ForeignKey(StaffModel, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return self.name


class ExpenseModel(models.Model):
    """"""
    type = models.ForeignKey(ExpenseTypeModel, on_delete=models.CASCADE)
    amount = models.FloatField()
    FLOW = (
        ('', '----------'), ('outgoing', 'OUTGOING'), ('incoming', 'INCOMING')
    )

    flow = models.CharField(max_length=100, choices=FLOW)
    remark = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    date = models.DateField(auto_now_add=True, null=True, blank=True)
    created_by = models.ForeignKey(StaffModel, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.type.name



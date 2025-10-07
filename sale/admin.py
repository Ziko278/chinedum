from django.contrib import admin
from sale.models import SaleModel, SaleSummaryModel, TransactionModel, LodgementModel


# Register your models here.
admin.site.register(SaleModel)
admin.site.register(SaleSummaryModel)
admin.site.register(TransactionModel)
admin.site.register(LodgementModel)


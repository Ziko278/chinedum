from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from datetime import date
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from staff.models import StaffModel
from staff.forms import StaffForm
from inventory.models import InventoryModel, StockInModel, StockOutModel
from inventory.forms import InventoryForm
from sale.models import SaleSummaryModel, SaleModel, TransactionModel
from expenses.models import ExpenseModel


class DashboardView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        today = date.today()
        sale_list =SaleSummaryModel.objects.filter(date__gte=today, date__lte=today)
        general_sale_list = SaleSummaryModel.objects.all()
        no_of_sale = sale_list.count()
        price_of_good = 0
        cost_of_good = 0
        no_of_item = 0
        debt_owed = 0
        total_debt_owed = 0
        expense_made = 0
        debt_refunded = 0

        for sale in sale_list:
            sale_id = sale.sale_id
            price_of_good += float(sale.amount_paid) + float(sale.current_balance)
            inventory_list = SaleModel.objects.filter(sale_id=sale_id)
            for inventory in inventory_list:
                cost_of_good += inventory.stock.unit_cost_price * inventory.quantity
                no_of_item += inventory.quantity

            debt_owed += sale.current_balance

        transaction_list = TransactionModel.objects.filter(transaction_type='refund', date__gte=today, date__lte=today)
        for transaction in transaction_list:
            debt_refunded += transaction.cash_refund

        for general_sale in general_sale_list:
            total_debt_owed += general_sale.current_balance

        profit_from_good = price_of_good - cost_of_good

        expense_list = ExpenseModel.objects.filter(date__gte=today, date__lte=today)
        for expense in expense_list:
            expense_made += expense.amount

        context['no_of_sale'] = no_of_sale
        context['cost_of_good'] = cost_of_good
        context['no_of_item'] = no_of_item
        context['price_of_good'] = price_of_good
        context['profit_from_good'] = profit_from_good
        context['debt_owed'] = debt_owed
        context['total_debt_owed'] = total_debt_owed
        context['expense_made'] = expense_made
        context['debt_refunded'] = debt_refunded
        return context

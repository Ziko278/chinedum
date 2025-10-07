from django.shortcuts import render, redirect
from django.urls import reverse
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from django.contrib.messages.views import SuccessMessageMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from staff.models import StaffModel
from staff.forms import StaffForm
from customer.models import CustomerModel, SaleRepModel
from customer.forms import CustomerForm, SaleRepForm
from django.contrib import messages
from sale.models import TransactionModel, SaleModel, SaleSummaryModel
from inventory.models import StockOutModel
from django.db.models import Sum, Max


# Create your views here.
class CustomerCreateView(SuccessMessageMixin, CreateView):
    model = CustomerModel
    form_class = CustomerForm
    template_name = 'customer/create.html'
    success_message = 'Customer Successfully Registered'

    def get_success_url(self):
        return reverse('customer_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class CustomerListView(ListView):
    model = CustomerModel
    fields = '__all__'
    paginate_by = 10
    template_name = 'customer/index.html'
    context_object_name = "customer_list"

    def get_queryset(self):
        return CustomerModel.objects.all().order_by('full_name')


class CustomerDetailView(DetailView):
    model = CustomerModel
    fields = '__all__'
    template_name = 'customer/detail.html'
    context_object_name = "customer"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer_pk = self.kwargs.get('pk')
        customer = CustomerModel.objects.get(pk=customer_pk)
        total_bought_worth = SaleSummaryModel.objects.filter(customer=customer).aggregate(Sum("grand_total"))
        total_bought = SaleSummaryModel.objects.filter(customer=customer).aggregate(Sum("total_crate"))
        transaction_list = TransactionModel.objects.filter(customer=customer).order_by("created_at").reverse()[:10]
        context['transaction_list'] = transaction_list
        context['total_bought_worth'] = total_bought_worth
        context['total_bought'] = total_bought
        return context


class CustomerUpdateView(SuccessMessageMixin, UpdateView):
    model = CustomerModel
    form_class = CustomerForm
    template_name = 'customer/edit.html'
    success_message = 'Customer Detail Successfully Updated'

    def get_success_url(self):
        return reverse('customer_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer_pk = self.kwargs.get('pk')
        customer = CustomerModel.objects.get(pk=customer_pk)
        context['customer'] = customer
        return context


class CustomerDeleteView(SuccessMessageMixin, DeleteView):
    model = CustomerModel
    fields = '__all__'
    template_name = 'customer/delete.html'
    context_object_name = "customer"
    success_url = "../index"
    success_message = 'Customer Successfully Deleted'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer_pk = self.kwargs.get('pk')

        return context


class CustomerSummaryView(SuccessMessageMixin, TemplateView):
    template_name = 'customer/summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        customer_list = CustomerModel.objects.all()
        no_of_customer = customer_list.count()
        total_amount_bought = 0
        total_credit = 0
        total_bought_worth = SaleSummaryModel.objects.filter(client_type='customer').aggregate(Sum("grand_total"))
        total_crate_owed = SaleSummaryModel.objects.filter(client_type='customer').aggregate(Sum("crate_owed"))
        total_bought = SaleSummaryModel.objects.filter(client_type='customer').aggregate(Sum("total_crate"))
        total_sold_worth = SaleSummaryModel.objects.filter(client_type='customer').aggregate(Sum("grand_total"))
        highest_buying_customer = CustomerModel.objects.order_by("amount_bought").reverse()
        if highest_buying_customer:
            highest_buying_customer = highest_buying_customer[0]
        for customer in customer_list:
            total_amount_bought += customer.amount_bought
            total_credit += customer.balance

        context['no_of_customer'] = no_of_customer
        context['highest_buying_customer'] = highest_buying_customer
        context['total_bought_worth'] = total_bought_worth
        context['total_crate_owed'] = total_crate_owed
        context['total_sold_worth'] = total_sold_worth
        context['total_bought'] = total_bought
        context['total_amount_bought'] = round(total_amount_bought)
        context['total_credit'] = round(total_credit)

        return context


class SaleRepCreateView(SuccessMessageMixin, CreateView):
    model = SaleRepModel
    form_class = SaleRepForm
    template_name = 'sale_rep/create.html'
    success_message = 'Sale Rep Successfully Registered'

    def get_success_url(self):
        return reverse('sale_rep_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class SaleRepListView(ListView):
    model = SaleRepModel
    fields = '__all__'
    paginate_by = 10
    template_name = 'sale_rep/index.html'
    context_object_name = "sale_rep_list"


class SaleRepDetailView(DetailView):
    model = SaleRepModel
    fields = '__all__'
    template_name = 'sale_rep/detail.html'
    context_object_name = "sale_rep"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sale_rep_pk = self.kwargs.get('pk')
        sale_rep = SaleRepModel.objects.get(pk=sale_rep_pk)
        total_bought_worth = SaleSummaryModel.objects.filter(sale_rep=sale_rep).aggregate(Sum("grand_total"))
        total_bought = SaleSummaryModel.objects.filter(sale_rep=sale_rep).aggregate(Sum("total_crate"))
        transaction_list = TransactionModel.objects.filter(sale_rep=sale_rep).order_by("created_at").reverse()[:10]
        context['transaction_list'] = transaction_list
        context['total_bought_worth'] = total_bought_worth
        context['total_bought'] = total_bought
        return context


class SaleRepUpdateView(SuccessMessageMixin, UpdateView):
    model = SaleRepModel
    form_class = SaleRepForm
    template_name = 'sale_rep/edit.html'
    success_message = 'Sale Rep Details Successfully Updated'

    def get_success_url(self):
        return reverse('sale_rep_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sale_rep_pk = self.kwargs.get('pk')
        sale_rep = SaleRepModel.objects.get(pk=sale_rep_pk)
        context['sale_rep'] = sale_rep
        return context


class SaleRepDeleteView(SuccessMessageMixin, DeleteView):
    model = SaleRepModel
    fields = '__all__'
    template_name = 'sale_rep/delete.html'
    context_object_name = "sale_rep"
    success_url = "../index"
    success_message = 'Sale Rep Successfully Deleted'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sale_rep_pk = self.kwargs.get('pk')

        return context


class SaleRepSummaryView(SuccessMessageMixin, TemplateView):
    template_name = 'sale_rep/summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        sale_rep_list = SaleRepModel.objects.all()
        no_of_sale_rep = sale_rep_list.count()
        total_crate_owed = SaleSummaryModel.objects.filter(client_type='sale_rep').aggregate(Sum("crate_owed"))
        total_bought = SaleSummaryModel.objects.filter(client_type='sale_rep').aggregate(Sum("total_crate"))
        highest_buying_customer = SaleRepModel.objects.order_by("total_amount_bought").reverse()
        if highest_buying_customer:
            highest_buying_customer = highest_buying_customer[0]
        total_max_credit = 0
        total_credit = 0
        for sale_rep in sale_rep_list:
            total_max_credit += sale_rep.max_credit
            total_credit += sale_rep.credit

        context['no_of_sale_rep'] = no_of_sale_rep
        context['total_bought'] = total_bought
        context['highest_buying_customer'] = highest_buying_customer
        context['total_crate_owed'] = total_crate_owed
        context['total_max_credit'] = round(total_max_credit)
        context['total_credit'] = round(total_credit)

        return context

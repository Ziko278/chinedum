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
from expenses.models import ExpenseTypeModel, ExpenseModel
from expenses.forms import ExpenseTypeForm, ExpenseForm


# Create your views here.
class ExpenseTypeCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ExpenseTypeModel
    form_class = ExpenseTypeForm
    template_name = 'expense_type/create.html'
    success_message = 'Expense Type Successfully Registered'

    def get_success_url(self):
        return reverse('expense_type_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ExpenseTypeListView(LoginRequiredMixin, ListView):
    model = ExpenseTypeModel
    fields = '__all__'
    paginate_by = 10
    template_name = 'expense_type/index.html'
    context_object_name = "expense_type_list"


class ExpenseTypeDetailView(LoginRequiredMixin, DetailView):
    model = ExpenseTypeModel
    fields = '__all__'
    template_name = 'expense_type/detail.html'
    context_object_name = "expense_type"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expense_type_pk = self.kwargs.get('pk')
        expense_type = ExpenseTypeModel.objects.get(pk=expense_type_pk)
        expense_list = ExpenseModel.objects.filter(type=expense_type).order_by("created_at").reverse()[0:10]
        total_expense = 0
        for expense in expense_list:
            total_expense += expense.amount

        context['expense_list'] = expense_list
        context['total_expense'] = total_expense
        return context


class ExpenseTypeUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ExpenseTypeModel
    form_class = ExpenseTypeForm
    template_name = 'expense_type/edit.html'
    success_message = 'Expense Type Successfully Updated'

    def get_success_url(self):
        return reverse('expense_type_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ExpenseTypeDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = ExpenseTypeModel
    fields = '__all__'
    template_name = 'expense_type/delete.html'
    context_object_name = "expense_type"
    success_url = "../index"
    success_message = 'Expense Type Successfully Deleted'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expense_type_pk = self.kwargs.get('pk')
        expense_type = ExpenseTypeModel.objects.get(pk=expense_type_pk)

        return context


class ExpenseCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = ExpenseModel
    form_class = ExpenseForm
    template_name = 'expense/create.html'
    success_message = 'Expense Successfully Registered'

    def get_success_url(self):
        return reverse('expense_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ExpenseListView(LoginRequiredMixin, ListView):
    model = ExpenseModel
    fields = '__all__'
    paginate_by = 10
    template_name = 'expense/index.html'
    context_object_name = "expense_list"

    def get_queryset(self):
        expense = ExpenseModel.objects.all().order_by("created_at").reverse()
        return expense


class ExpenseDetailView(LoginRequiredMixin, DetailView):
    model = ExpenseModel
    fields = '__all__'
    template_name = 'expense/detail.html'
    context_object_name = "expense"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class ExpenseUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = ExpenseModel
    form_class = ExpenseForm
    template_name = 'expense/edit.html'
    success_message = 'Expense Successfully Updated'

    def get_success_url(self):
        return reverse('expense_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expense_pk = self.kwargs.get('pk')
        expense = ExpenseModel.objects.get(pk=expense_pk)
        context['expense'] = expense
        return context


class ExpenseDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = ExpenseModel
    fields = '__all__'
    template_name = 'expense/delete.html'
    context_object_name = "expense"
    success_url = "../index"
    success_message = 'Expense Successfully Deleted'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        expense_pk = self.kwargs.get('pk')
        expense = ExpenseModel.objects.get(pk=expense_pk)
        context['expense'] = expense

        return context


class ExpenseSummaryView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    template_name = 'expense/summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context

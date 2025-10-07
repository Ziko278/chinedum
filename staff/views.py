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
from sale.models import SaleSummaryModel, TransactionModel
from django.db.models import Sum


# Create your views here.
class StaffCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = StaffModel
    form_class = StaffForm
    template_name = 'staff/create.html'
    success_message = 'Staff Successfully Registered'

    def get_success_url(self):
        return reverse('staff_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class StaffListView(LoginRequiredMixin, ListView):
    model = StaffModel
    fields = '__all__'
    paginate_by = 10
    template_name = 'staff/index.html'
    context_object_name = "staff_list"


class StaffDetailView(LoginRequiredMixin, DetailView):
    model = StaffModel
    fields = '__all__'
    template_name = 'staff/detail.html'
    context_object_name = "staff"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staff_pk = self.kwargs.get('pk')
        staff = StaffModel.objects.get(pk=staff_pk)
        transaction_list = TransactionModel.objects.filter(created_by=staff).order_by("created_at").reverse()[:15]
        context['transaction_list'] = transaction_list
        return context


class StaffUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = StaffModel
    form_class = StaffForm
    template_name = 'staff/edit.html'
    success_message = 'Staff Information Successfully Updated'

    def get_success_url(self):
        return reverse('staff_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class StaffDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = StaffModel
    fields = '__all__'
    template_name = 'staff/delete.html'
    context_object_name = "staff"
    success_url = "../index"
    success_message = 'Staff Successfully Deleted'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staff_pk = self.kwargs.get('pk')
        staff = StaffModel.objects.get(pk=staff_pk)

        return context


class StaffSummaryView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    template_name = 'staff/summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        staff_list = StaffModel.objects.all()
        no_of_staff = staff_list.count()
        monthly_salary = 0
        for staff in staff_list:
            monthly_salary += staff.salary

        context['no_of_staff'] = no_of_staff
        context['monthly_salary'] = round(monthly_salary)
        context['avg_monthly_salary'] = round(monthly_salary/no_of_staff)

        return context

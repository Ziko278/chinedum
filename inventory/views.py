from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
from django.db.models import Sum, Avg
import json
from django.contrib import messages
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
from inventory.models import InventoryModel, StockInModel, StockOutModel, StockOutCrateModel
from inventory.forms import InventoryForm
from sale.models import TransactionModel, SaleModel, SaleSummaryModel


class InventoryCreateView(LoginRequiredMixin, SuccessMessageMixin, CreateView):
    model = InventoryModel
    form_class = InventoryForm
    template_name = 'inventory/create.html'
    success_message = 'Inventory Successfully Registered'

    def get_success_url(self):
        return reverse('inventory_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context


class InventoryListView(LoginRequiredMixin, ListView):
    model = InventoryModel
    fields = '__all__'
    paginate_by = 15
    template_name = 'inventory/index.html'
    context_object_name = "inventory_list"

    def get_queryset(self):
        return InventoryModel.objects.all().order_by('name')


class InventoryDetailView(LoginRequiredMixin, DetailView):
    model = InventoryModel
    fields = '__all__'
    template_name = 'inventory/detail.html'
    context_object_name = "inventory"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inventory_pk = self.kwargs.get('pk')
        inventory = InventoryModel.objects.get(pk=inventory_pk)
        active_stock_list = StockInModel.objects.filter(inventory=inventory, status='active')
        finished_stock_list = StockInModel.objects.filter(inventory=inventory, status='finished')
        stock_out_list = StockOutModel.objects.filter(inventory=inventory).order_by('created_at').reverse()[:15]

        worth_in_store = inventory.quantity_left * inventory.selling_price
        total_bought = StockInModel.objects.filter(inventory=inventory).aggregate(Sum("quantity_bought"))
        total_sold = SaleModel.objects.filter(inventory=inventory).aggregate(Sum("quantity"))
        total_damage = StockOutModel.objects.filter(inventory=inventory).aggregate(Sum("quantity"))
        total_worth_bought = StockInModel.objects.filter(inventory=inventory).aggregate(Sum("total_cost_price"))
        total_sold_worth = SaleModel.objects.filter(inventory=inventory).aggregate(Sum("total_price"))
        total_worth_damaged = StockOutModel.objects.filter(inventory=inventory).aggregate(Sum("worth"))
        if not total_worth_damaged['worth__sum']:
            total_worth_damaged['worth__sum'] = 0
        if not total_sold_worth['total_price__sum']:
            total_sold_worth['total_price__sum'] = 0
        if not total_worth_bought['total_cost_price__sum']:
            total_worth_bought['total_cost_price__sum'] = 0
        total_profit = (total_sold_worth['total_price__sum'] + worth_in_store) - (total_worth_damaged['worth__sum'] + total_worth_bought['total_cost_price__sum'])

        context['active_stock_list'] = active_stock_list
        context['finished_stock_list'] = finished_stock_list
        context['stock_out_list'] = stock_out_list
        context['worth_in_store'] = worth_in_store
        context['total_bought'] = total_bought
        context['total_sold'] = total_sold
        context['total_damage'] = total_damage
        context['total_worth_bought'] = total_worth_bought
        context['total_sold_worth'] = total_sold_worth
        context['total_worth_damaged'] = total_worth_damaged
        context['total_profit'] = total_profit
        return context


class InventoryUpdateView(LoginRequiredMixin, SuccessMessageMixin, UpdateView):
    model = InventoryModel
    form_class = InventoryForm
    template_name = 'inventory/edit.html'
    success_message = 'Inventory Successfully Updated'

    def get_success_url(self):
        return reverse('inventory_detail', kwargs={'pk': self.object.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inventory_pk = self.kwargs.get('pk')
        inventory = InventoryModel.objects.get(pk=inventory_pk)
        context['inventory'] = inventory
        return context


class InventoryDeleteView(LoginRequiredMixin, SuccessMessageMixin, DeleteView):
    model = InventoryModel
    fields = '__all__'
    template_name = 'inventory/delete.html'
    context_object_name = "inventory"
    success_url = "../index"
    success_message = 'Inventory Successfully Deleted'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inventory_pk = self.kwargs.get('pk')

        return context


def inventory_date_report_view(request, string):
    stat_type = request.POST['statistic_type']
    if stat_type == 'month':
        pass
    elif stat_type == 'date':
        start_date = end_date = request.POST['start_date']
    elif stat_type == 'range':
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
    else:
        pass
    inventory_list = InventoryModel.objects.all().order_by('name')
    report_list = []
    total_sale = 0
    total_profit = 0
    for inventory in inventory_list:
        quantity = SaleModel.objects.filter(inventory=inventory, date__gte=start_date, date__lte=end_date).aggregate(Sum("quantity"))
        avg_cost_price = StockInModel.objects.filter(inventory=inventory).aggregate(Avg("unit_cost_price"))
        avg_selling_price = SaleModel.objects.filter(inventory=inventory, date__gte=start_date, date__lte=end_date).aggregate(Avg("unit_selling_price"))
        total_selling_price = SaleModel.objects.filter(inventory=inventory, date__gte=start_date, date__lte=end_date).aggregate(Sum("total_price"))
        profit = 0
        if total_selling_price['total_price__sum'] and avg_cost_price['unit_cost_price__avg'] and quantity[
            'quantity__sum']:
            profit = total_selling_price['total_price__sum'] - (
                        avg_cost_price['unit_cost_price__avg'] * quantity['quantity__sum'])

        detail = {'name': inventory.name,
                  'quantity': quantity,
                  'cost_price': avg_cost_price,
                  'selling_price': avg_selling_price,
                  'total_price': total_selling_price,
                  'profit': profit
                  }
        report_list.append(detail)
        if total_selling_price['total_price__sum']:
            total_sale += float(total_selling_price['total_price__sum'])
        total_profit += profit

    context = {}
    context['report_list'] = report_list
    context['total_profit'] = total_profit
    context['total_sale'] = total_sale
    context['start_date'] = start_date
    context['end_date'] = end_date
    context['type'] = stat_type

    return render(request, 'inventory/date_report.html', context=context)


class InventoryReportView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    template_name = 'inventory/report.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        inventory_list = InventoryModel.objects.all().order_by('name')
        report_list = []
        total_sale = 0
        total_profit = 0
        for inventory in inventory_list:
            quantity = SaleModel.objects.filter(inventory=inventory).aggregate(Sum("quantity"))
            avg_cost_price = StockInModel.objects.filter(inventory=inventory).aggregate(Avg("unit_cost_price"))
            avg_selling_price = SaleModel.objects.filter(inventory=inventory).aggregate(Avg("unit_selling_price"))
            total_selling_price = SaleModel.objects.filter(inventory=inventory).aggregate(Sum("total_price"))
            profit = 0
            if total_selling_price['total_price__sum'] and avg_cost_price['unit_cost_price__avg'] and quantity['quantity__sum']:
                profit = total_selling_price['total_price__sum'] - (avg_cost_price['unit_cost_price__avg'] * quantity['quantity__sum'])

            detail = {'name': inventory.name,
                      'quantity': quantity,
                      'cost_price': avg_cost_price,
                      'selling_price': avg_selling_price,
                      'total_price': total_selling_price,
                      'profit': profit
                      }
            report_list.append(detail)
            if total_selling_price['total_price__sum']:
                total_sale += float(total_selling_price['total_price__sum'])
            total_profit += profit

        context['report_list'] = report_list
        context['total_profit'] = total_profit
        context['total_sale'] = total_sale
        return context


class InventorySummaryView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    template_name = 'inventory/summary.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        worth_in_store = 0
        inventory_list = InventoryModel.objects.all()
        for inventory in inventory_list:
            worth_in_store += inventory.quantity_left * inventory.selling_price
        no_of_item = InventoryModel.objects.all().aggregate(Sum("quantity_left"))
        no_of_empty = InventoryModel.objects.all().aggregate(Sum("empty"))
        total_bought = StockInModel.objects.all().aggregate(Sum("quantity_bought"))
        total_sold = SaleModel.objects.all().aggregate(Sum("quantity"))
        total_damage = StockOutModel.objects.all().aggregate(Sum("quantity"))
        total_worth_bought = StockInModel.objects.all().aggregate(Sum("total_cost_price"))
        total_sold_worth = SaleModel.objects.all().aggregate(Sum("total_price"))
        total_worth_damaged = StockOutModel.objects.all().aggregate(Sum("worth"))
        if not total_worth_damaged['worth__sum']:
            total_worth_damaged['worth__sum'] = 0
        if not total_sold_worth['total_price__sum']:
            total_sold_worth['total_price__sum'] = 0
        if not total_worth_bought['total_cost_price__sum']:
            total_worth_bought['total_cost_price__sum'] = 0
        total_profit = (total_sold_worth['total_price__sum'] + worth_in_store) - (total_worth_damaged['worth__sum'] + total_worth_bought['total_cost_price__sum'])

        context['worth_in_store'] = worth_in_store
        context['no_of_item'] = no_of_item
        context['no_of_empty'] = no_of_empty
        context['total_bought'] = total_bought
        context['total_sold'] = total_sold
        context['total_damage'] = total_damage
        context['total_worth_bought'] = total_worth_bought
        context['total_sold_worth'] = total_sold_worth
        context['total_worth_damaged'] = total_worth_damaged
        context['total_profit'] = total_profit

        return context


@login_required
def inventory_add_empty_view(request, pk):
    if request.method == 'POST':
        quantity = float(request.POST['quantity'])
        inventory_pk = request.POST['inventory']
        inventory = InventoryModel.objects.get(pk=inventory_pk)
        inventory.empty += quantity
        inventory.save()

        messages.success(request, str(quantity) + ' crate of ' + inventory.name + ' successfully added')
        return redirect(reverse('inventory_detail', kwargs={'pk': inventory.pk}))

    inventory = InventoryModel.objects.get(pk=pk)

    context = {
        'inventory': inventory
    }

    return render(request, 'inventory/add_empty.html', context=context)


@login_required
def single_stock_in_create_view(request, pk):
    if request.method == 'POST':
        inventory = request.POST['inventory']
        quantity_bought = float(request.POST['quantity_bought'])
        unit_cost_price = float(request.POST['unit_cost_price'])
        total_cost_price = float(request.POST['total_cost_price'])
        empty = float(request.POST['empty'])

        last_stock_in_object = StockInModel.objects.last()
        if not last_stock_in_object:
            batch = 1
        else:
            batch = int(last_stock_in_object.batch) + 1

        inventory = InventoryModel.objects.get(pk=inventory)
        stock_in = StockInModel.objects.create(inventory=inventory, quantity_bought=quantity_bought,
                                                   quantity_left=quantity_bought, unit_cost_price=unit_cost_price,
                                                   total_cost_price=total_cost_price, batch=batch, empty=empty)
        stock_in.save()

        if stock_in.id:
            inventory_previous_quantity = inventory.quantity_left
            inventory_current_quantity = inventory_previous_quantity + quantity_bought
            inventory.quantity_left = inventory_current_quantity
            inventory.empty -= empty
            inventory.save()

        messages.success(request, str(quantity_bought) + ' CRATES OF ' + inventory.name + ' STOCKED IN SUCCESSFULLY')
        request.session['inventory_batch'] = batch
        return redirect(reverse('stock_in_index'))

    inventory = InventoryModel.objects.get(pk=pk)
    last_stock = StockInModel.objects.filter(inventory=inventory)
    if last_stock:
        cost_price = last_stock.last().unit_cost_price
    else:
        cost_price = ''

    context = {
        'inventory': inventory,
        'cost_price': cost_price
    }

    return render(request, 'stock_in/single_create.html', context=context)


@login_required
def stock_in_index_view(request):
    if request.method == 'POST':
        inventory_batch = request.session['inventory_batch']
        stock_list = StockInModel.objects.filter(batch=inventory_batch)
        context = {
            'stock_list': stock_list
        }
        return render(request, 'stock_in/index.html', context=context)

    stock_list = StockInModel.objects.all().order_by("created_at").reverse()[0:20]
    context = {
        'stock_list': stock_list
    }
    return render(request, 'stock_in/index.html', context=context)


@login_required
def stock_in_create_view(request):
    if request.method == 'POST':
        inventory_list = request.POST.getlist('inventory[]')
        quantity_bought_list = request.POST.getlist('quantity_bought[]')
        unit_cost_price_list = request.POST.getlist('unit_cost_price[]')
        total_cost_price_list = request.POST.getlist('unit_cost_price[]')

        last_stock_in_object = StockInModel.objects.last()
        if not last_stock_in_object:
            batch = 1
        else:
            batch = last_stock_in_object.batch + 1

        for num in range(len(inventory_list)):
            inventory_quantity_bought = quantity_bought_list[num]
            unit_cost_price = unit_cost_price_list[num]
            total_cost_price = total_cost_price_list[num]

            inventory = InventoryModel.objects.get(pk=inventory_list[num])
            stock_in = StockInModel.objects.create(inventory=inventory, quantity_bought=inventory_quantity_bought,
                                                   quantity_left=inventory_quantity_bought, unit_cost_price=unit_cost_price,
                                                   total_cost_price=total_cost_price, batch=batch)
            stock_in.save()

            if stock_in.id:
                inventory_previous_quantity = inventory.quantity_left
                inventory_current_quantity = inventory_previous_quantity + inventory_quantity_bought
                inventory.quantity_left = inventory_current_quantity
                inventory.save()

        request.session['inventory_batch'] = batch
        return redirect(reverse('stock_in_index'))

    inventory_list = InventoryModel.objects.all()

    context = {
        'inventory_list': inventory_list
    }

    return render(request, 'stock_in/create.html', context=context)


@login_required
def stock_in_edit_view(request, pk):
    if request.method == 'POST':
        stock_pk = request.POST['stock']
        quantity_bought = float(request.POST['quantity_bought'])
        unit_cost_price = float(request.POST['unit_cost_price'])
        total_cost_price = float(request.POST['total_cost_price'])
        empty = float(request.POST['empty'])

        stock = StockInModel.objects.get(pk=stock_pk)

        inventory = stock.inventory
        inventory.quantity_left = inventory.quantity_left - stock.quantity_bought + quantity_bought
        inventory.empty = inventory.empty + stock.empty - empty
        inventory.save()

        stock.quantity_bought = quantity_bought
        stock.quantity_left = quantity_bought
        stock.unit_cost_price = unit_cost_price
        stock.total_cost_price = total_cost_price
        stock.empty = empty
        stock.save()

        messages.success(request, 'STOCK DETAIL SUCCESSFULLY UPDATED')
        return redirect(reverse('stock_in_detail', kwargs={'pk': stock.pk}))

    stock = StockInModel.objects.get(pk=pk)
    if stock.quantity_bought > stock.quantity_left:
        return redirect(reverse('stock_in_detail', kwargs={'pk': stock.pk}))

    context = {
        'stock': stock
    }

    return render(request, 'stock_in/edit.html', context=context)


@login_required
def stock_in_delete_view(request, pk):
    if request.method == 'POST':
        stock_pk = request.POST['stock']
        stock = StockInModel.objects.get(pk=stock_pk)

        inventory = stock.inventory
        inventory.quantity_left -= stock.quantity_bought
        inventory.empty += stock.empty
        inventory.save()

        stock.delete()

        messages.success(request, 'STOCK SUCCESSFULLY DELETED')
        return redirect(reverse('inventory_detail', kwargs={'pk': inventory.pk}))

    stock = StockInModel.objects.get(pk=pk)
    if stock.quantity_bought > stock.quantity_left:
        return redirect(reverse('stock_in_detail', kwargs={'pk': stock.pk}))

    context = {
        'stock': stock
    }

    return render(request, 'stock_in/delete.html', context=context)


class StockInDetailView(LoginRequiredMixin, SuccessMessageMixin, TemplateView):
    template_name = 'stock_in/detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        stock_pk = self.kwargs.get('pk')
        stock = StockInModel.objects.get(pk=stock_pk)
        worth_in_store = float(stock.quantity_left * stock.inventory.selling_price)
        total_sold = SaleModel.objects.filter(stock=stock).aggregate(Sum("quantity"))
        total_damage = StockOutModel.objects.filter(stock=stock).aggregate(Sum("quantity"))
        total_sold_worth = SaleModel.objects.filter(stock=stock).aggregate(Sum("total_price"))
        total_worth_damaged = StockOutModel.objects.filter(stock=stock).aggregate(Sum("worth"))
        if not total_worth_damaged['worth__sum']:
            total_worth_damaged['worth__sum'] = 0
        if not total_sold['quantity__sum']:
            total_sold['quantity__sum'] = 0
        total_profit = (float(worth_in_store) + float(total_sold['quantity__sum'])) - (float(stock.total_cost_price) + float(total_worth_damaged['worth__sum']))

        context['stock'] = stock
        context['total_sold'] = total_sold
        context['total_damage'] = total_damage
        context['worth_in_store'] = worth_in_store
        context['total_sold_worth'] = total_sold_worth
        context['total_worth_damaged'] = total_worth_damaged
        context['total_profit'] = total_profit

        return context


@login_required
def stock_out_view(request, pk):
    if request.method == 'POST':
        stock_id = request.POST['stock_id']
        stock = StockInModel.objects.get(id=stock_id)
        quantity_to_stock_out = float(request.POST['quantity'])
        worth = quantity_to_stock_out * stock.unit_cost_price
        empty = float(request.POST['empty'])
        purpose = request.POST['purpose']
        restock_crate = quantity_to_stock_out - empty

        if quantity_to_stock_out > stock.quantity_left:
            return redirect(reverse('inventory_detail', kwargs={'pk': stock.inventory.pk}))
        if empty > quantity_to_stock_out:
            return redirect(reverse('inventory_detail', kwargs={'pk': stock.inventory.pk}))
        stock.quantity_left -= quantity_to_stock_out
        if stock.quantity_left == 0:
            stock.status = 'finished'
        stock.save()

        stock_out = StockOutModel.objects.create(stock=stock, inventory=stock.inventory, quantity=quantity_to_stock_out, worth=worth, empty=empty, remark=purpose)
        stock_out.save()
        if stock_out.id:
            inventory = stock.inventory
            inventory.quantity_left -= quantity_to_stock_out
            inventory.empty += restock_crate
            inventory.save()
            messages.success(request, str(quantity_to_stock_out) + ' CRATES OF ' + inventory.name + ' STOCKED OUT SUCCESSFULLY')
            return redirect(reverse('inventory_detail', kwargs={'pk': stock.inventory.pk}))
        messages.error(request, 'FAILED TO STOCK OUT THE INVENTORY, TRY LATER')
        return redirect(reverse('inventory_detail', kwargs={'pk': stock.inventory.pk}))

    stock = StockInModel.objects.get(pk=pk)
    context = {
        'stock': stock
    }

    return render(request, 'stock_in/stock_out.html', context=context)


@login_required
def stock_out_empty_view(request, pk):
    if request.method == 'POST':
        inventory_id = request.POST['inventory_id']
        inventory = InventoryModel.objects.get(id=inventory_id)
        quantity = float(request.POST['quantity'])
        purpose = request.POST['purpose']

        if quantity > inventory.quantity_left:
            return redirect(reverse('inventory_detail', kwargs={'pk': inventory.pk}))

        inventory.empty -= quantity
        inventory.save()
        stock_out = StockOutCrateModel.objects.create(inventory=inventory, remark=purpose, quantity=quantity)
        stock_out.save()
        if stock_out.id:
            messages.success(request, str(quantity) + ' EMPTY CRATES OF ' + inventory.name + ' STOCKED OUT SUCCESSFULLY')
            return redirect(reverse('inventory_detail', kwargs={'pk': inventory.pk}))
        messages.error(request, 'FAILED TO STOCK OUT EMPTY CRATES, TRY LATER')
        return redirect(reverse('inventory_detail', kwargs={'pk': inventory.pk}))

    inventory = InventoryModel.objects.get(pk=pk)
    context = {
        'inventory': inventory
    }
    return render(request, 'stock_in/stock_out_empty.html', context=context)


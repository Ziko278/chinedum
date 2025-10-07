from django.shortcuts import render, redirect, HttpResponse
from django.urls import reverse
import json
from django.contrib import messages
from django.db.models import Sum, Avg
import time
from datetime import date, timedelta, datetime
from django.core.serializers.json import DjangoJSONEncoder
from django.core import serializers
from expenses.models import ExpenseModel
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
from sale.models import SaleModel, SaleSummaryModel, TransactionModel, LodgementModel
from customer.models import CustomerModel, SaleRepModel


# Create your views here.
@login_required
def sale_create_view(request):
    if request.method == 'POST':
        client_type = request.POST['client_type']
        inventory_list = request.POST.getlist('product_id[]')
        quantity_bought_list = request.POST.getlist('quantity_input[]')
        selling_price_list = request.POST.getlist('selling_price[]')
        crate_brought_list = request.POST.getlist('crate_brought[]')
        crate_remaining_list = request.POST.getlist('crate_remaining[]')
        grand_total = float(request.POST['grand_total'])
        transfer_paid = float(request.POST['transfer_paid'])
        cash_paid = float(request.POST['amount_paid'])
        amount_paid = cash_paid + transfer_paid
        current_balance = request.POST['balance']
        client_detail = request.POST['customer_detail']
        user_id = request.POST['user']
        user = StaffModel.objects.get(pk=user_id)
        previous_balance = 0
        total_crate = 0
        crate_owed = 0

        last_sale_object = SaleSummaryModel.objects.last()
        if not last_sale_object:
            sale_id = 1
        else:
            sale_id = last_sale_object.sale_id + 1

        crate_balance = 0
        for num in range(len(inventory_list)):
            crate_balance += float(crate_remaining_list[num])
            total_crate += float(crate_brought_list[num])
            crate_owed += float(crate_remaining_list[num])

        if client_type == 'customer':
            customer_id = request.POST['customer']
            customer = CustomerModel.objects.get(pk=customer_id)
            previous_balance = float(customer.balance)
            customer.balance += float(current_balance)
            customer.amount_bought += float(grand_total)
            customer.crate_balance += float(crate_balance)
            customer.save()
            client_detail = ''
        else:
            customer = ''

        for num in range(len(inventory_list)):
            inventory_quantity_bought = float(quantity_bought_list[num])
            unit_selling_price = float(selling_price_list[num])
            total_price = unit_selling_price * inventory_quantity_bought
            crate_brought = crate_brought_list[num]
            crate_remaining = crate_remaining_list[num]

            inventory = InventoryModel.objects.get(pk=inventory_list[num])
            inventory.quantity_left -= float(quantity_bought_list[num])
            inventory.empty += float(crate_brought)
            inventory.owed_empty += float(crate_remaining)
            inventory.save()
            stock_list = StockInModel.objects.filter(inventory=inventory, status='active')

            for stock in stock_list:
                if stock.quantity_left >= float(inventory_quantity_bought):
                    stock_quantity_bought = float(stock.quantity_left) - inventory_quantity_bought
                    stock_total_price = inventory_quantity_bought * unit_selling_price
                    stock.quantity_left -= float(inventory_quantity_bought)
                    if stock.quantity_left == 0:
                        stock.status = 'finished'
                    stock.save()

                    sale = SaleModel.objects.create(inventory=inventory, stock=stock, sale_id=sale_id, quantity=inventory_quantity_bought, unit_selling_price=unit_selling_price, total_price=stock_total_price, crate_brought=crate_brought, crate_remaining=crate_remaining, created_by=user)
                    sale.save()
                    break
                else:
                    stock_quantity_bought = float(stock.quantity_left)
                    stock_total_price = stock_quantity_bought * unit_selling_price
                    inventory_quantity_bought -= float(stock.quantity_left)
                    stock.quantity_left = 0
                    stock.status = 'finished'
                    stock.save()

                    sale = SaleModel.objects.create(inventory=inventory, stock=stock, sale_id=sale_id, quantity=stock_quantity_bought, unit_selling_price=unit_selling_price, total_price=stock_total_price, crate_brought=crate_brought, crate_remaining=crate_remaining, created_by=user)
                    sale.save()

        if client_type == 'customer':
            sale_summary = SaleSummaryModel.objects.create(sale_id=sale_id, previous_balance=previous_balance, grand_total=grand_total, total_crate=total_crate,
                                                       amount_paid=amount_paid, current_balance=current_balance, client_detail=client_detail, crate_owed=crate_owed,
                                                     customer=customer, client_type=client_type, created_by=user, cash_paid=cash_paid, transfer_paid=transfer_paid)
        else:
            sale_summary = SaleSummaryModel.objects.create(sale_id=sale_id, previous_balance=previous_balance, crate_owed=crate_owed,
                                                           grand_total=grand_total, total_crate=total_crate,
                                                           amount_paid=amount_paid, current_balance=current_balance,
                                                           client_detail=client_detail, client_type=client_type, created_by=user,
                                                           transfer_paid=transfer_paid, cash_paid=cash_paid)

        sale_summary.save()
        if sale_summary.id:
            if client_type == 'customer':
                transaction = TransactionModel.objects.create(transaction_type='sale', client_type=client_type, customer=customer, sale=sale_summary, total_balance=customer.balance, total_crate_balance=customer.crate_balance, created_by=user)
            else:
                transaction = TransactionModel.objects.create(transaction_type='sale', client_type=client_type, client_detail=client_detail, sale=sale_summary, total_balance=grand_total, total_crate_balance=total_crate, created_by=user)
            transaction.save()

        messages.success(request, 'SALE SUCCESSFUL')
        request.session['sale_id'] = sale_id
        return redirect(reverse('sale_index'))

    customer_list = CustomerModel.objects.all()
    inventory_list = InventoryModel.objects.all()
    serialized_inventory_list = serializers.serialize("json", inventory_list)
    customer_list = serializers.serialize("json", customer_list)

    context = {
        'inventory_list': inventory_list,
        'customer_list': customer_list,
        'serialized_inventory_list': serialized_inventory_list
    }

    return render(request, 'sale/create.html', context=context)


@login_required
def sale_rep_sale_create_view(request):
    if request.method == 'POST':
        client_type = request.POST['client_type']
        inventory_list = request.POST.getlist('product_id[]')
        quantity_bought_list = request.POST.getlist('quantity_input[]')
        selling_price_list = request.POST.getlist('selling_price[]')
        crate_brought_list = request.POST.getlist('crate_brought[]')
        crate_remaining_list = request.POST.getlist('crate_remaining[]')
        grand_total = request.POST['grand_total']
        transfer_paid = float(request.POST['transfer_paid'])
        cash_paid = float(request.POST['amount_paid'])
        amount_paid = cash_paid + transfer_paid
        current_balance = request.POST['balance']
        client_detail = request.POST['customer_detail']
        user_id = request.POST['user']
        user = StaffModel.objects.get(pk=user_id)
        total_crate = 0
        crate_owed = 0

        last_sale_object = SaleSummaryModel.objects.last()
        if not last_sale_object:
            sale_id = 1
        else:
            sale_id = last_sale_object.sale_id + 1

        crate_balance = 0
        for num in range(len(inventory_list)):
            crate_balance += float(crate_remaining_list[num])
            total_crate += float(crate_brought_list[num])
            crate_owed += float(crate_remaining_list[num])

        customer_id = request.POST['customer']
        customer = SaleRepModel.objects.get(pk=customer_id)
        previous_balance = float(customer.credit)
        customer.credit += float(current_balance)
        customer.crate_credit += float(crate_balance)
        customer.save()
        client_detail = ''

        for num in range(len(inventory_list)):
            inventory_quantity_bought = float(quantity_bought_list[num])
            unit_selling_price = float(selling_price_list[num])
            total_price = unit_selling_price * inventory_quantity_bought
            crate_brought = crate_brought_list[num]
            crate_remaining = crate_remaining_list[num]

            inventory = InventoryModel.objects.get(pk=inventory_list[num])
            inventory.quantity_left -= float(quantity_bought_list[num])
            inventory.empty += float(crate_brought)
            inventory.owed_empty += float(crate_remaining)
            inventory.save()
            stock_list = StockInModel.objects.filter(inventory=inventory, status='active')
  
            for stock in stock_list:
                if stock.quantity_left >= float(inventory_quantity_bought):
                    stock_quantity_bought = float(stock.quantity_left) - inventory_quantity_bought
                    stock_total_price = inventory_quantity_bought * unit_selling_price
                    stock.quantity_left -= float(inventory_quantity_bought)
                    if stock.quantity_left == 0:
                        stock.status = 'finished'
                    stock.save()

                    sale = SaleModel.objects.create(inventory=inventory, stock=stock, sale_id=sale_id, quantity=inventory_quantity_bought, unit_selling_price=unit_selling_price, total_price=stock_total_price, crate_brought=crate_brought, crate_remaining=crate_remaining, created_by=user)
                    sale.save()
                    break
                else:
                    stock_quantity_bought = float(stock.quantity_left)
                    stock_total_price = stock_quantity_bought * unit_selling_price
                    inventory_quantity_bought -= float(stock.quantity_left)
                    stock.quantity_left = 0
                    stock.status = 'finished'
                    stock.save()

                    sale = SaleModel.objects.create(inventory=inventory, stock=stock, sale_id=sale_id, quantity=stock_quantity_bought, unit_selling_price=unit_selling_price, total_price=stock_total_price, crate_brought=crate_brought, crate_remaining=crate_remaining, created_by=user)
                    sale.save()

        sale_summary = SaleSummaryModel.objects.create(sale_id=sale_id, previous_balance=previous_balance, grand_total=grand_total,
                                                       amount_paid=amount_paid, current_balance=current_balance, client_detail=client_detail,
                                                     sale_rep=customer, client_type=client_type, total_crate=total_crate, crate_owed=crate_owed,
                                                       transfer_paid=transfer_paid, cash_paid=cash_paid, created_by=user)

        sale_summary.save()
        if sale_summary.id:
            transaction = TransactionModel.objects.create(transaction_type='sale', client_type=client_type, sale_rep=customer, sale=sale_summary,  total_balance=customer.credit, total_crate_balance=customer.crate_credit, created_by=user)
            transaction.save()

        messages.success(request, 'SALE SUCCESSFUL')
        request.session['sale_id'] = sale_id
        return redirect(reverse('sale_index'))

    customer_list = SaleRepModel.objects.all()
    inventory_list = InventoryModel.objects.all()
    serialized_inventory_list = serializers.serialize("json", inventory_list)
    customer_list = serializers.serialize("json", customer_list)

    context = {
        'inventory_list': inventory_list,
        'customer_list': customer_list,
        'serialized_inventory_list': serialized_inventory_list
    }

    return render(request, 'sale/sale_rep_create.html', context=context)


@login_required
def sale_index_view(request):
    if request.method == 'POST':
        start_date = end_date = request.POST['date']
    else:
        start_date = end_date = date.today()
    sale_list = SaleSummaryModel.objects.filter(date__gte=start_date, date__lte=end_date).order_by("created_at").reverse()
    sale_id = []
    for sale in sale_list:
        sale_id.append(sale.sale_id)
    sale_detail_list = SaleModel.objects.filter(sale_id__in=sale_id)
    
    
    context = {
        'sale_list': sale_list,
        'sale_detail_list': sale_detail_list,
        'date': start_date
    }
    return render(request, 'sale/index.html', context=context)


@login_required
def sale_debtor_view(request, string):
    if string == 'customer':
        debtor_list = CustomerModel.objects.filter(balance__gt=0).order_by("full_name")
    elif string == 'sale_rep':
        debtor_list = SaleRepModel.objects.filter(credit__gt=0).order_by("full_name")
    else:
        debtor_list = SaleSummaryModel.objects.filter(client_type='guest', current_balance__gt=0).order_by("client_detail")

    context = {
        'debtor_list': debtor_list,
        'debtor_type': string
    }
    return render(request, 'sale/debtor.html', context=context)


@login_required
def sale_debtor_payment_view(request, pk, string):
    if request.method == 'POST':
        debtor_type = request.POST['debtor_type']
        debtor_pk = request.POST['debtor']
        cash_balance = request.POST['cash_balance']
        crate_balance = request.POST['crate_balance']

        if not cash_balance:
            cash_balance = 0
        if not crate_balance:
            crate_balance = 0
        cash_balance = float(cash_balance)
        crate_balance = float(crate_balance)

        if debtor_type == 'customer':
            debtor = CustomerModel.objects.get(pk=debtor_pk)
            debtor.balance -= cash_balance
            debtor.crate_balance -= crate_balance
        elif debtor_type == 'sale_rep':
            debtor = SaleRepModel.objects.get(pk=debtor_pk)
            debtor.credit -= cash_balance
            debtor.crate_credit -= crate_balance
        else:
            debtor = SaleSummaryModel.objects.get(pk=debtor_pk)
            debtor.amount_paid += cash_balance
            debtor.current_balance -= cash_balance
            debtor.crate_owed -= crate_balance

        debtor.save()

        if debtor_type == 'customer':
            transaction = TransactionModel.objects.create(transaction_type='refund', client_type=debtor_type,
                        customer=debtor, total_balance=debtor.balance, total_crate_balance=debtor.crate_balance,
                        cash_refund=cash_balance, crate_refund=crate_balance)
        elif debtor_type == 'sale_rep':
            transaction = TransactionModel.objects.create(transaction_type='refund', client_type=debtor_type, sale_rep=debtor,
                                                          total_balance=debtor.credit, total_crate_balance=debtor.crate_credit,
                                                          cash_refund=cash_balance, crate_refund=crate_balance)
        else:
            transaction = TransactionModel.objects.create(transaction_type='refund', client_type=debtor_type, cash_refund=cash_balance, crate_refund=crate_balance,
                                                          total_balance=debtor.current_balance, total_crate_balance=debtor.crate_owed, client_detail=debtor.client_detail, sale=debtor)
        transaction.save()
        messages.success(request, 'REFUND SUCCESSFUL')
    if string == 'customer':
        debtor = CustomerModel.objects.get(pk=pk)
    elif string == 'sale_rep':
        debtor = SaleRepModel.objects.get(pk=pk)
    else:
        debtor = SaleSummaryModel.objects.filter(sale_id=pk).first()

    context = {
        'customer': debtor,
        'debtor_type': string
    }
    return render(request, 'sale/pay_debt.html', context=context)


@login_required
def sale_cash_flow_report_view(request, string):
    if 'date' in request.POST:
        today = request.POST['date']
        today = datetime.strptime(today, '%Y-%m-%d')
    else:
        today = date.today()

    if today == date.today():
        is_today = True
    else:
        is_today = False
    yesterday = today - timedelta(days=1)


    total_cash_from_sale = SaleSummaryModel.objects.filter(date__gte=today, date__lte=today).aggregate(Sum("grand_total"))
    total_transfer_from_sale = SaleSummaryModel.objects.filter(date__gte=today, date__lte=today).aggregate(Sum("transfer_paid"))
    total_debt_owed = SaleSummaryModel.objects.filter(date__gte=today, date__lte=today).aggregate(Sum("current_balance"))
    total_debt_refunded = TransactionModel.objects.filter(transaction_type='refund', date__gte=today, date__lte=today).aggregate(Sum("cash_refund"))
    out_going_expenses = ExpenseModel.objects.filter(flow='outgoing', date__gte=today, date__lte=today).aggregate(Sum("amount"))
    in_coming_expenses = ExpenseModel.objects.filter(flow='incoming', date__gte=today, date__lte=today).aggregate(Sum("amount"))
    previous_lodgement = LodgementModel.objects.filter(date__gte=yesterday, date__lte=yesterday)

    if previous_lodgement:
        previous_till = previous_lodgement[0].present_till
    else:
        previous_till = 0

    if not total_cash_from_sale['grand_total__sum']:
        total_cash_from_sale['grand_total__sum'] = 0
    if not total_debt_refunded['cash_refund__sum']:
        total_debt_refunded['cash_refund__sum'] = 0
    if not in_coming_expenses['amount__sum']:
        in_coming_expenses['amount__sum'] = 0
    if not total_transfer_from_sale['transfer_paid__sum']:
        total_transfer_from_sale['transfer_paid__sum'] = 0
    if not total_debt_owed['current_balance__sum']:
        total_debt_owed['current_balance__sum'] = 0
    if not out_going_expenses['amount__sum']:
        out_going_expenses['amount__sum'] = 0

    total_cash_at_hand = total_cash_from_sale['grand_total__sum'] + total_debt_refunded['cash_refund__sum'] + in_coming_expenses['amount__sum'] + previous_till
    total_out_flow = total_transfer_from_sale['transfer_paid__sum'] + total_debt_owed['current_balance__sum'] + out_going_expenses['amount__sum']
    lodgement = total_cash_at_hand - total_out_flow

    if 'lodgement' in request.POST:
        money_kept = float(request.POST['lodgement'])
        staff_pk = request.POST['user']
        present_still = lodgement - money_kept
        staff = StaffModel.objects.get(pk=staff_pk)

        current_lodgement = LodgementModel.objects.filter(date__gte=today, date__lte=today)
        if current_lodgement:
            current_lodgement = current_lodgement[0]
            current_lodgement.lodgement = money_kept
            current_lodgement.present_till = present_still
            current_lodgement.save()
        else:
            current_lodgement = LodgementModel.objects.create(lodgement=money_kept, present_till=present_still, created_by=staff)
            current_lodgement.save()
        messages.success(request, 'LODGEMENT SAVED SUCCESSFUL')

    current_lodgement = LodgementModel.objects.filter(date__gte=today, date__lte=today)
    if current_lodgement:
        present_till = current_lodgement[0].present_till
        lodgement = current_lodgement[0].lodgement
    else:
        present_till = 0

    context = {
        'in_coming_expenses': in_coming_expenses,
        'out_going_expenses': out_going_expenses,
        'total_debt_owed': total_debt_owed,
        'total_debt_refunded': total_debt_refunded,
        'total_cash_from_sale': total_cash_from_sale,
        'total_transfer_from_sale': total_transfer_from_sale,
        'present_till': present_till,
        'previous_till': previous_till,
        'total_cash_at_hand': total_cash_at_hand,
        'total_out_flow': total_out_flow,
        'lodgement': lodgement,
        'report_type': string,
        'is_today': is_today,
        'today': today
    }
    return render(request, 'dashboard/cash_flow_report.html', context=context)


def today_sale_statistic_report_view(request):
    today = date.today()
    sale_list = SaleSummaryModel.objects.filter(date__gte=today, date__lte=today)
    general_sale_list = SaleSummaryModel.objects.all()
    no_of_sale = sale_list.count()
    price_of_good = 0
    cost_of_good = 0
    no_of_item = 0
    debt_owed = 0
    total_debt_owed = 0
    expense_made = 0
    income_made = 0
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

    expense_list = ExpenseModel.objects.filter(date__gte=today, date__lte=today, flow='outgoing')
    income_list = ExpenseModel.objects.filter(date__gte=today, date__lte=today, flow='incoming')

    for expense in expense_list:
        expense_made += expense.amount
    for income in income_list:
        income_made += income.amount
    context = {
    }
    context['start_date'] = context['end_date'] = today
    context['no_of_sale'] = no_of_sale
    context['cost_of_good'] = cost_of_good
    context['no_of_item'] = no_of_item
    context['price_of_good'] = price_of_good
    context['profit_from_good'] = profit_from_good
    context['debt_owed'] = debt_owed
    context['total_debt_owed'] = total_debt_owed
    context['expense_made'] = expense_made
    context['income_made'] = income_made
    context['debt_refunded'] = debt_refunded
    context['transfer'] = SaleSummaryModel.objects.filter(date__gte=today, date__lte=today).aggregate(Sum("transfer_paid"))
    context['cash'] = SaleSummaryModel.objects.filter(date__gte=today, date__lte=today).aggregate(Sum("cash_paid"))
    context['final_profit'] = profit_from_good - expense_made + income_made
    return render(request, 'dashboard/today_statistic_report.html', context=context)


def sale_statistic_report_view(request, string):
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
    sale_list = SaleSummaryModel.objects.filter(date__gte=start_date, date__lte=end_date)
    general_sale_list = SaleSummaryModel.objects.all()
    no_of_sale = sale_list.count()
    price_of_good = 0
    cost_of_good = 0
    no_of_item = 0
    debt_owed = 0
    total_debt_owed = 0
    expense_made = 0
    income_made = 0
    debt_refunded = 0

    for sale in sale_list:
        sale_id = sale.sale_id
        price_of_good += float(sale.amount_paid) + float(sale.current_balance)
        inventory_list = SaleModel.objects.filter(sale_id=sale_id)
        for inventory in inventory_list:
            cost_of_good += inventory.stock.unit_cost_price * inventory.quantity
            no_of_item += inventory.quantity

        debt_owed += sale.current_balance

    transaction_list = TransactionModel.objects.filter(transaction_type='refund', date__gte=start_date, date__lte=end_date)
    for transaction in transaction_list:
        debt_refunded += transaction.cash_refund

    for general_sale in general_sale_list:
        total_debt_owed += general_sale.current_balance

    profit_from_good = price_of_good - cost_of_good

    expense_list = ExpenseModel.objects.filter(date__gte=start_date, date__lte=end_date, flow='outgoing')
    income_list = ExpenseModel.objects.filter(date__gte=start_date, date__lte=end_date, flow='incoming')

    for expense in expense_list:
        expense_made += expense.amount
    for income in income_list:
        income_made += income.amount
    context = {
    }
    context['start_date'] = start_date
    context['end_date'] = end_date
    context['type'] = stat_type
    context['no_of_sale'] = no_of_sale
    context['cost_of_good'] = cost_of_good
    context['no_of_item'] = no_of_item
    context['price_of_good'] = price_of_good
    context['profit_from_good'] = profit_from_good
    context['debt_owed'] = debt_owed
    context['total_debt_owed'] = total_debt_owed
    context['expense_made'] = expense_made
    context['income_made'] = income_made
    context['debt_refunded'] = debt_refunded
    context['transfer'] = SaleSummaryModel.objects.filter(date__gte=start_date, date__lte=end_date).aggregate(Sum("transfer_paid"))
    context['cash'] = SaleSummaryModel.objects.filter(date__gte=start_date, date__lte=end_date).aggregate(Sum("cash_paid"))
    context['final_profit'] = profit_from_good - expense_made + income_made

    return render(request, 'dashboard/statistic_report.html', context=context)


@login_required
def customer_sale_transaction_view(request, pk, string):
    if string == 'customer':
        customer = CustomerModel.objects.get(pk=pk)
        transaction_list = TransactionModel.objects.filter(customer=customer).order_by("created_at").reverse()[0:20]
        client = customer
    elif string == 'sale_rep':
        sale_rep = SaleRepModel.objects.get(pk=pk)
        transaction_list = TransactionModel.objects.filter(sale_rep=sale_rep).order_by("created_at").reverse()[0:20]
        client = sale_rep
    else:
        transaction_list = SaleSummaryModel.objects.filter(client_type='guest', current_balance__gt=0).order_by("client_detail")[0:20]
        client = ''

    context = {
        'transaction_list': transaction_list,
        'transaction_type': string,
        'client': client
    }
    return render(request, 'sale/customer_transaction.html', context=context)


@login_required
def sale_transaction_view(request):
    transaction_list = TransactionModel.objects.all().order_by("created_at").reverse()[0:20]
    context = {
        'transaction_list': transaction_list,
    }
    return render(request, 'sale/transaction.html', context=context)


@login_required
def stock_out_create_view(request):
    if request.method == 'POST':
        stock_id = request.POST['stock_id']
        stock = StockInModel.objects.get(id=stock_id)
        quantity_to_stock_out = request.POST['quantity']
        if quantity_to_stock_out > stock.quantity_left:
            return redirect(reverse('stock_in_index'))
        stock.quantity_left -= quantity_to_stock_out
        stock_out = StockOutModel.objects.create()
        stock_out.save()
        if stock_out.id:
            if stock.quantity_left == 0:
                stock.status = 'finished'
            stock.save()

            inventory = stock.inventory
            inventory.quantity_left -= quantity_to_stock_out
            inventory.save()

            messages.success(request, 'STOCK OUT SUCCESSFUL')
            return redirect(reverse('stock_out_index'))
        return redirect(reverse('stock_out_index'))

    stock_list = StockInModel.objects.filter(status='active')
    context = {
        'stock_list': stock_list
    }

    return render(request, 'stock_out/create.html', context=context)


@login_required
def sale_detail_view(request, pk):
    sale = SaleSummaryModel.objects.get(sale_id=pk)
    sale_detail_list = SaleModel.objects.filter(sale_id__in=[pk])
    context = {
        'sale': sale,
        'sale_detail_list': sale_detail_list
    }
    return render(request, 'sale/detail.html', context=context)


@login_required
def sale_print_receipt_view(request, pk):
    sale = SaleSummaryModel.objects.get(sale_id=pk)
    sale_detail_list = SaleModel.objects.filter(sale_id__in=[pk])
    context = {
        'sale': sale,
        'sale_detail_list': sale_detail_list
    }
    return render(request, 'sale/print_receipt.html', context=context)


def sale_edit_view(request, pk):  
    if request.method == 'POST':
        previous_sale = SaleSummaryModel.objects.get(sale_id=pk)
        
        if previous_sale.client_type == 'customer':
            customer = previous_sale.customer
            customer.balance -= float(previous_sale.current_balance)
            customer.amount_bought -= float(previous_sale.grand_total)
            customer.crate_balance -= float(previous_sale.crate_owed)
            previous_balance = customer.balance
            customer.save()

        else:
            previous_balance = 0

        sale_list = SaleModel.objects.filter(sale_id__in=[pk])
        for sale in sale_list:
            inventory = sale.inventory
            inventory.quantity_left += float(sale.quantity)
            inventory.empty -= float(sale.crate_brought)
            inventory.owed_empty -= float(sale.crate_remaining)
            inventory.save()

            stock = sale.stock
            stock.quantity_left += float(sale.quantity)
            stock.status = 'active'
            stock.save()

            sale.delete()

        client_type = request.POST['client_type']
        inventory_list = request.POST.getlist('product_id[]')
        quantity_bought_list = request.POST.getlist('quantity_input[]')
        selling_price_list = request.POST.getlist('selling_price[]')
        crate_brought_list = request.POST.getlist('crate_brought[]')
        crate_remaining_list = request.POST.getlist('crate_remaining[]')
        grand_total = float(request.POST['grand_total'])
        transfer_paid = float(request.POST['transfer_paid'])
        cash_paid = float(request.POST['amount_paid'])
        amount_paid = cash_paid + transfer_paid
        current_balance = request.POST['balance']
        client_detail = request.POST['customer_detail']
        user_id = request.POST['user']
        user = StaffModel.objects.get(pk=user_id)
        previous_balance = 0
        total_crate = 0
        crate_owed = 0

        sale_id = pk

        crate_balance = 0
        for num in range(len(inventory_list)):
            crate_balance += float(crate_remaining_list[num])
            total_crate += float(crate_brought_list[num])
            crate_owed += float(crate_remaining_list[num])

        if client_type == 'customer':
            customer_id = request.POST['customer']
            customer = CustomerModel.objects.get(pk=customer_id)
            customer.balance += float(current_balance)
            customer.amount_bought += float(grand_total)
            customer.crate_balance += float(crate_balance)
            customer.save()
            client_detail = ''
        else:
            customer = ''

        for num in range(len(inventory_list)):
            inventory_quantity_bought = float(quantity_bought_list[num])
            unit_selling_price = float(selling_price_list[num])
            total_price = unit_selling_price * inventory_quantity_bought
            crate_brought = crate_brought_list[num]
            crate_remaining = crate_remaining_list[num]

            inventory = InventoryModel.objects.get(pk=inventory_list[num])
            inventory.quantity_left -= float(quantity_bought_list[num])
            inventory.empty += float(crate_brought)
            inventory.owed_empty += float(crate_remaining)
            inventory.save()
            stock_list = StockInModel.objects.filter(inventory=inventory, status='active')

            for stock in stock_list:
                if stock.quantity_left >= float(inventory_quantity_bought):
                    stock_quantity_bought = float(stock.quantity_left) - inventory_quantity_bought
                    stock_total_price = inventory_quantity_bought * unit_selling_price
                    stock.quantity_left -= float(inventory_quantity_bought)
                    if stock.quantity_left == 0:
                        stock.status = 'finished'
                    stock.save()

                    new_sale = SaleModel.objects.create(inventory=inventory, stock=stock, sale_id=sale_id, quantity=inventory_quantity_bought, unit_selling_price=unit_selling_price, total_price=stock_total_price, crate_brought=crate_brought, crate_remaining=crate_remaining, created_by=user)
                    new_sale.save()
                    break
                else:
                    stock_quantity_bought = float(stock.quantity_left)
                    stock_total_price = stock_quantity_bought * unit_selling_price
                    inventory_quantity_bought -= float(stock.quantity_left)
                    stock.quantity_left = 0
                    stock.status = 'finished'
                    stock.save()

                    new_sale = SaleModel.objects.create(inventory=inventory, stock=stock, sale_id=sale_id, quantity=stock_quantity_bought, unit_selling_price=unit_selling_price, total_price=stock_total_price, crate_brought=crate_brought, crate_remaining=crate_remaining, created_by=user)
                    new_sale.save()

        sale_summary = SaleSummaryModel.objects.get(sale_id=pk)
        sale_summary.previous_balance = previous_balance
        sale_summary.grand_total = grand_total
        sale_summary.total_crate = total_crate
        sale_summary.amount_paid = amount_paid
        sale_summary.current_balance = current_balance
        sale_summary.crate_owed = crate_owed
        sale_summary.transfer_paid = transfer_paid
        sale_summary.cash_paid = cash_paid
        sale_summary.created_by = user
        sale_summary.client_detail = client_detail
        sale_summary.client_type = client_type
        sale_summary.save()

        if client_type == 'customer':
            sale_summary.customer = customer

        if sale_summary.id:
            if client_type == 'customer':
                transaction = TransactionModel.objects.create(transaction_type='sale_edit', client_type=client_type, customer=customer, sale=sale_summary, total_balance=customer.balance, total_crate_balance=customer.crate_balance, created_by=user)
            else:
                transaction = TransactionModel.objects.create(transaction_type='sale_edit', client_type=client_type, client_detail=client_detail, sale=sale_summary, total_balance=grand_total, total_crate_balance=total_crate, created_by=user)
            transaction.save()

        messages.success(request, 'SALE EDITED SUCCESSFUL')
        request.session['sale_id'] = sale_id
        return redirect(reverse('sale_detail', kwargs={'pk': pk}))

    customer_list = CustomerModel.objects.all()
    inventory_list = InventoryModel.objects.all()
    serialized_inventory_list = serializers.serialize("json", inventory_list)
    customer_list = serializers.serialize("json", customer_list)
    sale = SaleSummaryModel.objects.get(sale_id=pk)

    context = {
        'inventory_list': inventory_list,
        'customer_list': customer_list,
        'serialized_inventory_list': serialized_inventory_list,
        'sale': sale,
        'sale_detail_list': SaleModel.objects.filter(sale_id__in=[pk])
    }

    return render(request, 'sale/edit.html', context=context)


@login_required
def sale_rep_edit_view(request, pk):
    if request.method == 'POST':
        previous_sale = SaleSummaryModel.objects.get(sale_id=pk)
        customer = previous_sale.sale_rep
        customer.credit -= float(previous_sale.current_balance)
        customer.total_amount_bought -= float(previous_sale.grand_total)
        customer.crate_credit -= float(previous_sale.crate_owed)
        previous_balance = customer.credit
        customer.save()

        sale_list = SaleModel.objects.filter(sale_id__in=[pk])
        for sale in sale_list:
            inventory = sale.inventory
            inventory.quantity_left += float(sale.quantity)
            inventory.empty -= float(sale.crate_brought)
            inventory.owed_empty -= float(sale.crate_remaining)
            inventory.save()

            stock = sale.stock
            stock.quantity_left += float(sale.quantity)
            stock.status = 'active'
            stock.save()

            sale.delete()
            
        client_type = request.POST['client_type']
        inventory_list = request.POST.getlist('product_id[]')
        quantity_bought_list = request.POST.getlist('quantity_input[]')
        selling_price_list = request.POST.getlist('selling_price[]')
        crate_brought_list = request.POST.getlist('crate_brought[]')
        crate_remaining_list = request.POST.getlist('crate_remaining[]')
        grand_total = request.POST['grand_total']
        transfer_paid = float(request.POST['transfer_paid'])
        cash_paid = float(request.POST['amount_paid'])
        amount_paid = cash_paid + transfer_paid
        current_balance = request.POST['balance']
        client_detail = request.POST['customer_detail']
        user_id = request.POST['user']
        user = StaffModel.objects.get(pk=user_id)
        total_crate = 0
        crate_owed = 0

        sale_id = pk

        crate_balance = 0
        for num in range(len(inventory_list)):
            crate_balance += float(crate_remaining_list[num])
            total_crate += float(crate_brought_list[num])
            crate_owed += float(crate_remaining_list[num])

        customer_id = request.POST['customer']
        customer = SaleRepModel.objects.get(pk=customer_id)
        previous_balance = float(customer.credit)
        customer.total_amount_bought += float(grand_total)
        customer.credit += float(current_balance)
        customer.crate_credit += float(crate_balance)
        customer.save()
        client_detail = ''

        for num in range(len(inventory_list)):
            inventory_quantity_bought = float(quantity_bought_list[num])
            unit_selling_price = float(selling_price_list[num])
            total_price = unit_selling_price * inventory_quantity_bought
            crate_brought = crate_brought_list[num]
            crate_remaining = crate_remaining_list[num]

            inventory = InventoryModel.objects.get(pk=inventory_list[num])
            inventory.quantity_left -= float(quantity_bought_list[num])
            inventory.empty += float(crate_brought)
            inventory.owed_empty += float(crate_remaining)
            inventory.save()
            
            stock_list = StockInModel.objects.filter(inventory=inventory, status='active')

            for stock in stock_list:
                if stock.quantity_left >= float(inventory_quantity_bought):
                    stock_quantity_bought = float(stock.quantity_left) - inventory_quantity_bought
                    stock_total_price = inventory_quantity_bought * unit_selling_price
                    stock.quantity_left -= float(inventory_quantity_bought)
                    if stock.quantity_left == 0:
                        stock.status = 'finished'
                    stock.save()

                    sale = SaleModel.objects.create(inventory=inventory, stock=stock, sale_id=sale_id, quantity=inventory_quantity_bought, unit_selling_price=unit_selling_price, total_price=stock_total_price, crate_brought=crate_brought, crate_remaining=crate_remaining, created_by=user)
                    sale.save()
                    break
                else:
                    stock_quantity_bought = float(stock.quantity_left)
                    stock_total_price = stock_quantity_bought * unit_selling_price
                    inventory_quantity_bought -= float(stock.quantity_left)
                    stock.quantity_left = 0
                    stock.status = 'finished'
                    stock.save()

                    sale = SaleModel.objects.create(inventory=inventory, stock=stock, sale_id=sale_id, quantity=stock_quantity_bought, unit_selling_price=unit_selling_price, total_price=stock_total_price, crate_brought=crate_brought, crate_remaining=crate_remaining, created_by=user)
                    sale.save()

        sale_summary = SaleSummaryModel.objects.get(sale_id=pk)
        sale_summary.previous_balance = previous_balance
        sale_summary.grand_total = grand_total
        sale_summary.total_crate = total_crate
        sale_summary.amount_paid = amount_paid
        sale_summary.current_balance = current_balance
        sale_summary.crate_owed = crate_owed
        sale_summary.transfer_paid = transfer_paid
        sale_summary.cash_paid = cash_paid
        sale_summary.created_by = user
        sale_summary.client_detail = client_detail
        sale_summary.client_type = client_type
        sale_summary.sale_rep = customer
        sale_summary.save()

        if sale_summary.id:
            transaction = TransactionModel.objects.create(transaction_type='sale_edit', client_type=client_type, sale_rep=customer, sale=sale_summary,  total_balance=customer.credit, total_crate_balance=customer.crate_credit, created_by=user)
            transaction.save()

        messages.success(request, 'SALE EDITED SUCCESSFUL')
        request.session['sale_id'] = sale_id
        return redirect(reverse('sale_detail', kwargs={'pk': pk}))

    customer_list = SaleRepModel.objects.all()
    inventory_list = InventoryModel.objects.all()
    serialized_inventory_list = serializers.serialize("json", inventory_list)
    customer_list = serializers.serialize("json", customer_list)
    sale = SaleSummaryModel.objects.get(sale_id=pk)

    context = {
        'inventory_list': inventory_list,
        'customer_list': customer_list,
        'serialized_inventory_list': serialized_inventory_list,
        'sale': sale,
        'sale_detail_list': SaleModel.objects.filter(sale_id__in=[pk])
    }

    return render(request, 'sale/sale_rep_edit.html', context=context)

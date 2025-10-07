from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from sale.views import sale_create_view, sale_index_view, sale_detail_view, sale_print_receipt_view,  \
    sale_rep_sale_create_view, sale_transaction_view, sale_debtor_view, customer_sale_transaction_view, \
    sale_debtor_payment_view,  today_sale_statistic_report_view,  sale_cash_flow_report_view, sale_statistic_report_view, \
    sale_rep_edit_view, sale_edit_view

urlpatterns = [
    path('create', sale_create_view, name='sale_create'),
    path('sale-rep/create', sale_rep_sale_create_view, name='sale_rep_sale_create'),

    path('index', sale_index_view, name='sale_index'),
    path('index/<int:year>/<int:month>/<int:day>', sale_index_view, name='sale_date_index'),
    path('<int:pk>/detail', sale_detail_view, name='sale_detail'),
    path('<int:pk>/edit', sale_edit_view, name='sale_edit'),
    path('sale-rep/<int:pk>/edit', sale_rep_edit_view, name='sale_rep_sale_edit'),
    path('<int:pk>/receipt/print', sale_print_receipt_view, name='sale_print_receipt'),

    path('transaction', sale_transaction_view, name='sale_transaction'),
    path('transaction/<int:pk>/?P<string>[\w\-]+', customer_sale_transaction_view, name='customer_sale_transaction'),
    path('cash-flow/report', sale_cash_flow_report_view, name='today_cash_flow_report'),
    path('cash-flow/report/?P<string>[\w\-]+', sale_cash_flow_report_view, name='cash_flow_report'),
    path('statistic/report', today_sale_statistic_report_view, name='today_statistic_report'),
    path('statistic/report/?P<string>[\w\-]+', sale_statistic_report_view, name='statistic_report'),

    path('debtors/?P<string>[\w\-]+', sale_debtor_view, name='sale_debtors'),
    path('debtors/<int:pk>/?P<string>[\w\-]+/payment', sale_debtor_payment_view, name='sale_debtor_payment'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

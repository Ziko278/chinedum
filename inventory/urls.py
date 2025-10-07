from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from inventory.views import InventoryCreateView, InventoryListView, InventoryDetailView, InventoryUpdateView,\
    InventoryDeleteView, InventoryReportView, stock_in_create_view, single_stock_in_create_view, stock_in_index_view,  stock_out_view,\
    stock_out_empty_view, stock_in_edit_view, stock_in_delete_view, \
    InventorySummaryView, StockInDetailView, inventory_add_empty_view, inventory_date_report_view #, ExpenseListView, ExpenseDetailView,
# ExpenseUpdateView, ExpenseDeleteView


urlpatterns = [
    path('create', InventoryCreateView.as_view(), name='inventory_create'),
    path('index', InventoryListView.as_view(), name='inventory_index'),
    path('<int:pk>/detail', InventoryDetailView.as_view(), name='inventory_detail'),
    path('<int:pk>/edit', InventoryUpdateView.as_view(), name='inventory_edit'),
    path('<int:pk>/delete', InventoryDeleteView.as_view(), name='inventory_delete'),
    path('<int:pk>/empty/add', inventory_add_empty_view, name='inventory_add_empty'),
    path('summary', InventorySummaryView.as_view(), name='inventory_summary'),
    path('report', InventoryReportView.as_view(), name='inventory_report'),
    path('report/?P<string>[\w\-]+', inventory_date_report_view, name='inventory_date_report'),

    path('stock-in/create', stock_in_create_view, name='stock_in_create'),
    path('stock-in/<int:pk>/create', single_stock_in_create_view, name='single_stock_in_create'),
    path('stock-in/index', stock_in_index_view, name='stock_in_index'),
    path('stock-in/<int:pk>/detail', StockInDetailView.as_view(), name='stock_in_detail'),
    path('stock-in/<int:pk>/edit', stock_in_edit_view, name='stock_in_edit'),
    path('stock-in/<int:pk>/delete', stock_in_delete_view, name='stock_in_delete'),

    path('stock-out/<int:pk>', stock_out_view, name='stock_out'),
    path('stock-out/<int:pk>/empty', stock_out_empty_view, name='stock_out_empty')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

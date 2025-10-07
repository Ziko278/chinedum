from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from customer.views import CustomerCreateView, CustomerListView, CustomerDetailView, CustomerUpdateView,\
    CustomerDeleteView, SaleRepCreateView, SaleRepListView, SaleRepDetailView, SaleRepUpdateView, SaleRepDeleteView,\
    SaleRepSummaryView, CustomerSummaryView


urlpatterns = [
    path('create', CustomerCreateView.as_view(), name='customer_create'),
    path('index', CustomerListView.as_view(), name='customer_index'),
    path('<int:pk>/detail', CustomerDetailView.as_view(), name='customer_detail'),
    path('<int:pk>/edit', CustomerUpdateView.as_view(), name='customer_edit'),
    path('<int:pk>/delete', CustomerDeleteView.as_view(), name='customer_delete'),
    path('summary', CustomerSummaryView.as_view(), name='customer_summary'),

    path('sale_rep/create', SaleRepCreateView.as_view(), name='sale_rep_create'),
    path('sale_rep/index', SaleRepListView.as_view(), name='sale_rep_index'),
    path('sale_rep/<int:pk>/detail', SaleRepDetailView.as_view(), name='sale_rep_detail'),
    path('sale_rep/<int:pk>/edit', SaleRepUpdateView.as_view(), name='sale_rep_edit'),
    path('sale_rep/<int:pk>/delete', SaleRepDeleteView.as_view(), name='sale_rep_delete'),
    path('sale_rep/summary', SaleRepSummaryView.as_view(), name='sale_rep_summary'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

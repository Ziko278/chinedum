from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from expenses.views import ExpenseTypeCreateView, ExpenseTypeListView, ExpenseTypeDetailView, ExpenseTypeUpdateView, ExpenseTypeDeleteView, ExpenseCreateView, ExpenseListView, ExpenseDetailView, ExpenseUpdateView, ExpenseDeleteView, ExpenseSummaryView


urlpatterns = [
    path('type/create', ExpenseTypeCreateView.as_view(), name='expense_type_create'),
    path('type/index', ExpenseTypeListView.as_view(), name='expense_type_index'),
    path('type/<int:pk>/detail', ExpenseTypeDetailView.as_view(), name='expense_type_detail'),
    path('type/<int:pk>/edit', ExpenseTypeUpdateView.as_view(), name='expense_type_edit'),
    path('type/<int:pk>/delete', ExpenseTypeDeleteView.as_view(), name='expense_type_delete'),

    path('create', ExpenseCreateView.as_view(), name='expense_create'),
    path('index', ExpenseListView.as_view(), name='expense_index'),
    path('<int:pk>/detail', ExpenseDetailView.as_view(), name='expense_detail'),
    path('<int:pk>/edit', ExpenseUpdateView.as_view(), name='expense_edit'),
    path('<int:pk>/delete', ExpenseDeleteView.as_view(), name='expense_delete'),
    path('summary', ExpenseSummaryView.as_view(), name='expense_summary'),

]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

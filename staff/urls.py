from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from staff.views import StaffCreateView, StaffListView, StaffDetailView, StaffUpdateView, StaffDeleteView, StaffSummaryView


urlpatterns = [
    path('create', StaffCreateView.as_view(), name='staff_create'),
    path('index', StaffListView.as_view(), name='staff_index'),
    path('<int:pk>/detail', StaffDetailView.as_view(), name='staff_detail'),
    path('<int:pk>/edit', StaffUpdateView.as_view(), name='staff_edit'),
    path('<int:pk>/delete', StaffDeleteView.as_view(), name='staff_delete'),
    path('summary', StaffSummaryView.as_view(), name='staff_summary'),


]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

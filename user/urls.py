from django.urls import path, include
from user.views import user_sign_in_view, user_sign_out_view, user_create_staff_account_view

urlpatterns = [
    path('account/create/staff/<int:pk>', user_create_staff_account_view, name='create_staff_account'),
    path('sign-in', user_sign_in_view, name='log_in'),
    path('sign-out', user_sign_out_view, name='log_out'),
]

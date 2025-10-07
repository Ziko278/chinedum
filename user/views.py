from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.urls import reverse
from django.views.generic import TemplateView
from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.generic.detail import DetailView
from user.models import UserRoleModel
from staff.models import StaffModel


def user_sign_in_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            user_role = UserRoleModel.objects.filter(user=user)[0]
            if user_role:
                request.session['user_role'] = user_role.role
                request.session['user_id'] = user_role.user.id

                messages.success(request, 'welcome back ' + user_role.staff.full_name)
                return redirect(reverse('dashboard'))

            else:
                return redirect(reverse('dashboard'))
        else:
            messages.error(request, 'Invalid Credentials')
            return redirect('../user/sign-in')

    return render(request, 'user/sign_in.html')


def user_sign_out_view(request):
    logout(request)
    return redirect('../user/sign-in')


@login_required
def user_create_staff_account_view(request, pk):
    user_exist = UserRoleModel.objects.filter(role='staff', staff=pk)

    if user_exist:
        messages.warning(request, 'Staff Account Already Activated')
        return redirect(reverse('staff_detail', kwargs={'pk': pk}))
    staff = StaffModel.objects.get(pk=pk)
    if staff.email:
        username = staff.email.lower()
        password = staff.email.lower()
        user = User.objects.create_user(username=username, password=password)
        user.is_active = True
        user.save()

        if user.id:
            user_role = UserRoleModel.objects.create(user=user, role=staff.position, staff=staff)
            user_role.save()
            if user_role.id:
                messages.success(request,
                                 f'Staff Account Has been Successfully Activated. username: {username}, password: {password}')
                return redirect(reverse('staff_detail', kwargs={'pk': pk}))
            else:
                user.delete()
                messages.warning(request, 'An unexpected error occurred, try later')
                return redirect(reverse('staff_detail', kwargs={'pk': pk}))
        else:
            messages.warning(request, 'Could not activate Staff Account, Try Later')
            return redirect(reverse('staff_detail', kwargs={'pk': pk}))
    else:
        messages.success(request, 'Fill in staff Email to create Account')
        return redirect(reverse('staff_detail', kwargs={'pk': pk}))



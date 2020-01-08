from django.shortcuts import render

# Create your views here.
from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST


from .models import Profile, Contact
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from common.decorators import ajax_required

@ajax_required
@require_POST
@login_required
def user_follow(request):
    user_id = request.POST.get('id')
    action = request.POST.get('action')
    if user_id and action:
        try:
            user = User.objects.get(id = user_id)
            if action == 'follow':
                Contact.objects.get_or_create(user_from = request.user, user_to = user)
            else:
                Contact.objects.filter(user_from = request.user, user_to = user).delete()
            return JsonResponse({"status":'ok'})
        except User.DoesNotExist:
            return JsonResponse({"status":"ok"})
    return JsonResponse({"status":"ok"})

@login_required
def user_list(request):
    users = User.objects.filter(is_active =True)
    return render(request,'account/user/list.html',{'section':'people','users':users})

@login_required
def user_detail(request,username):
    user = get_object_or_404(User, username=username, is_active = True)
    print(user.images_created.all())
    return render(request, 'account/user/detail.html',{'section':'people','user':user})

@login_required
def edit(request):
    if request.POST == 'POST':
        user_form = UserEditForm(instance=request.user, data=request.POST)
        profile_form = ProfileEditForm(
            instance=request.user, data=request.POST, file=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.successfully(request,'Profile updated successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile)
    return render(request, 'account/edit.html',{'user_form':user_form, 'profile_form':profile_form})

def registarion(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            return render(request, 'account/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})

@login_required
def dashboard(request):
    return render(request, 'account/dashboard.html', {'section': 'dashboard'})

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(
                request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated successfully')
                else:
                    return HttpResponse('Disabled acount')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})


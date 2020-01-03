from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from  .forms import ImageCreateForm
from .models import Image

# Create your views here.

@login_required
def image_create(request):
    if request.method =='POST':
        form = ImageCreateForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            new_item = form.save(commit = False)
            new_item.user = request.user
            new_item.save()
            return redirect(new_item.get_absolute_url())
    else:
        form = ImageCreateForm(data = request.GET)
    return render(request,'images/image/create.html',{'section':"images",'form':form})

def image_detail(request, id, slug):
    image = get_object_or_404(Image, id = id, slug = slug)
    return render(request,'images/image/detail.html',{'section':'images','image':image})

@login_required
@require_POST
def image_like(request):
    image_id = request.POST.get('id')
    action = request.POST.get('action')
    if image_id and action:
        try:
            image = Image.objects.get(id = image_id)
            if action == 'like':
                image.users_like.add(request.user)
            else:
                image.users_like.remove(request.user)
            return JsonResponse({'status':'ok'})
        except:
            pass
    return JsonResponse({'status':'ok'})

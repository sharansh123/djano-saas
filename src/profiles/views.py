from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
# Create your views here.

User = get_user_model()

@login_required
def profile_list_view(request):
    context = {
        "object_list": User.objects.filter(is_active=True)
    }
    return render(request, 'profiles/list.html', context)

@login_required
def profile_view(request, username=None, *args, **kwargs):
    user = request.user
    print(user.has_perm("view_user"))
    profile_user = get_object_or_404(User, username=username)
    return HttpResponse(f"Hello World {username}! - {profile_user.id}")

@login_required
def profile_detail_view(request, username=None, *args, **kwargs):
    profile_user = get_object_or_404(User, username=username)
    print(request.user.has_perm("view_user"))
    print(request.user)
    context = {
        "object": profile_user,
        "instance":profile_user,
        "owner" : True,
    }
    return render(request, 'profiles/detail.html', context)

from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, get_user_model

User = get_user_model()

# Create your views here.

def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username") or None
        password = request.POST.get("password") or None
        #print(username,password)
        if all([username,password]):
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                print("Logged In!")
                return redirect("/hello")
    return render(request, "auth/login.html", {})

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get("username") or None
        email = request.POST.get("email") or None
        password = request.POST.get("password") or None
        # user_exists = User.objects.filter(username__iexact=username).exists()
        # user_exists = User.objects.filter(username__iexact=username).exists()
        try:
            
            User.objects.create_user(username=username,email=email,password=password)
        except:
            pass
    return render(request,"auth/register.html", {})



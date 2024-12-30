from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from visits.models import PageVisit


def home_page_view(request, *args, **kwargs):
    page_visit = PageVisit.objects.filter(path=request.path)
    total_visit = PageVisit.objects.all()
    my_title = "My Page New"
    my_context = {
        "page_title":my_title,
        "page_visit":page_visit.count(),
        "total_visit": total_visit.count(),
    }
    PageVisit.objects.create(path=request.path)
    return render(request,"home.html", my_context)

VALID_CODE="1234"

def pw_protected_view(request, *args, **kwargs):
    is_allowed = request.session.get("protected_page_allowed") or 0
    print(request.session.get("protected_page_allowed"))
    if request.method == "POST":
        user_code = request.POST.get("code") or None
        if user_code == VALID_CODE:
            request.session["protected_page_allowed"] = 1
    if is_allowed:
        return render(request, "protected/view.html", {})
    return render(request,"protected/entry.html",{})

@login_required
def user_only_view(request, *args, **kwargs):
    return render(request, "protected/user-only.html",{})
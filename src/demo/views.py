from django.http import HttpResponse
from django.shortcuts import render

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
from django.urls import include, path
from . import views
urlpatterns = [
   path("<str:username>/",views.profile_detail_view),
   path("", views.profile_list_view)
]
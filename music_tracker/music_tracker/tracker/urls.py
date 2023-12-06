from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("albums/<str:year>", views.top_ten_list, name="top_ten"),
]

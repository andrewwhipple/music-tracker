from django.urls import path

from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("albums/<str:year>", views.top_ten_list, name="top_ten"),
    path("obsessions/<str:year>", views.obsessions_list, name="obsessions"),
    path("artist/<str:id>", views.artist_stats, name="artist_stats"),
    path("top-100/<str:year>", views.spotify_top_100_list, name="spotify_top_100"),
]

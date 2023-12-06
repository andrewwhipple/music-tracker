from django.contrib import admin

# Register your models here.
from music_tracker.tracker import models


@admin.register(models.Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "artist",
        "year",
        "listened",
        "priority",
        "original_rating",
        "rank",
    ]
    list_editable = ["listened", "priority", "original_rating", "rank"]
    list_filter = ["year", "listened", "priority"]


@admin.register(models.Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ["name"]


@admin.register(models.TopTenAlbumsList)
class TopTenAlbumsListAdmin(admin.ModelAdmin):
    list_display = ["title", "published"]
    list_editable = ["published"]

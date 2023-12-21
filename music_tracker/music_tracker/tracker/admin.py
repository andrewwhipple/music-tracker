from django.contrib import admin

# Register your models here.
from music_tracker.tracker import models


@admin.register(models.Album)
class AlbumAdmin(admin.ModelAdmin):
    list_display = [
        "title",
        "display_artists",
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


@admin.register(models.Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ["title", "album", "display_artists"]


@admin.register(models.ObsessionList)
class ObsessionListAdmin(admin.ModelAdmin):
    list_display = ["title", "published"]
    list_editable = ["published"]


@admin.register(models.ObsessionSongs)
class ObsessionSongAdmin(admin.ModelAdmin):
    list_display = ["song", "obsession_list", "ordering"]
    list_filter = ["obsession_list"]


@admin.register(models.SpotifyTop100List)
class SpotifyTop100ListAdmin(admin.ModelAdmin):
    list_display = ["title", "published"]
    list_editable = ["published"]


@admin.register(models.SpotifyTop100Songs)
class SpotifyTop100SongAdmin(admin.ModelAdmin):
    list_display = ["song", "top_100_list", "ordering"]
    list_filter = ["top_100_list"]

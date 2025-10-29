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
        "release_date",
    ]
    list_editable = ["listened", "priority", "original_rating", "rank"]
    list_filter = ["year", "listened", "priority"]
    search_fields = ["title", "artists__name"]


@admin.register(models.Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


@admin.register(models.TopTenAlbumsList)
class TopTenAlbumsListAdmin(admin.ModelAdmin):
    list_display = ["title", "published"]
    list_editable = ["published"]


@admin.register(models.Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ["title", "album", "display_artists"]
    search_fields = ["title", "artists__name"]


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


class ArtistAlbumRankingEntryInline(admin.TabularInline):
    model = models.ArtistAlbumRankingEntry
    extra = 0
    fields = ["rank", "album", "notes"]
    ordering = ["rank"]

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "album":
            # For existing objects, filter by the artist
            if hasattr(request, "_obj_") and request._obj_ and request._obj_.artist:
                kwargs["queryset"] = models.Album.objects.filter(
                    artists=request._obj_.artist
                )
            else:
                # For new objects, show all albums initially
                # The user will need to save after selecting an artist to get filtering
                kwargs["queryset"] = models.Album.objects.all()

        return super().formfield_for_foreignkey(db_field, request, **kwargs)


@admin.register(models.ArtistAlbumRanking)
class ArtistAlbumRankingAdmin(admin.ModelAdmin):
    list_display = ["artist", "published", "updated_at"]
    list_editable = ["published"]
    list_filter = ["published", "artist"]
    search_fields = ["artist__name"]
    inlines = [ArtistAlbumRankingEntryInline]

    def get_form(self, request, obj=None, **kwargs):
        # Store the object in the request so the inline can access it
        request._obj_ = obj
        return super().get_form(request, obj, **kwargs)

    def save_model(self, request, obj, form, change):
        super().save_model(request, obj, form, change)
        # After saving, update the object in the request for the inlines
        request._obj_ = obj


@admin.register(models.ArtistAlbumRankingEntry)
class ArtistAlbumRankingEntryAdmin(admin.ModelAdmin):
    list_display = ["ranking", "rank", "album", "notes"]
    list_filter = ["ranking__artist", "ranking"]
    search_fields = ["album__title", "ranking__artist__name"]
    ordering = ["ranking", "rank"]
